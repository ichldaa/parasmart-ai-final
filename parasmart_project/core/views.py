import json
import math
import re
import os
import requests
from collections import Counter

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import ParaphraseResult, PlagiarismCheck, UploadedFile


# ─────────────────────────────────────────────
# AUTH VIEWS
# ─────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Username atau password salah.')
    return render(request, 'core/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if password != password2:
            messages.error(request, 'Password tidak cocok.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah terdaftar.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('dashboard')
    return render(request, 'core/register.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ─────────────────────────────────────────────
# MAIN VIEWS
# ─────────────────────────────────────────────

@login_required
def dashboard_view(request):
    parafrase_count = ParaphraseResult.objects.filter(user=request.user).count()
    plagiarisme_count = PlagiarismCheck.objects.filter(user=request.user).count()
    upload_count = UploadedFile.objects.filter(user=request.user).count()
    return render(request, 'core/dashboard.html', {
        'parafrase_count': parafrase_count,
        'plagiarisme_count': plagiarisme_count,
        'upload_count': upload_count,
    })


@login_required
def parafrase_view(request):
    results = ParaphraseResult.objects.filter(user=request.user)[:5]
    return render(request, 'core/parafrase.html', {'results': results})


@login_required
def plagiarisme_view(request):
    checks = PlagiarismCheck.objects.filter(user=request.user)[:5]
    return render(request, 'core/plagiarisme.html', {'checks': checks})


@login_required
def upload_view(request):
    uploads = UploadedFile.objects.filter(user=request.user)[:5]
    return render(request, 'core/upload.html', {'uploads': uploads})


@login_required
def history_view(request):
    paraphrases = ParaphraseResult.objects.filter(user=request.user)
    plagiarisms = PlagiarismCheck.objects.filter(user=request.user)
    uploads = UploadedFile.objects.filter(user=request.user)
    return render(request, 'core/history.html', {
        'paraphrases': paraphrases,
        'plagiarisms': plagiarisms,
        'uploads': uploads,
    })


# ─────────────────────────────────────────────
# API VIEWS
# ─────────────────────────────────────────────

@login_required
@require_POST
def api_parafrase(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        style = data.get('style', 'formal')

        if not text:
            return JsonResponse({'error': 'Teks tidak boleh kosong.'}, status=400)

        if len(text) < 10:
            return JsonResponse({'error': 'Teks terlalu pendek.'}, status=400)

        # Panggil DeepSeek AI API
        api_key = settings.DEEPSEEK_API_KEY

        style_prompts = {
            'formal': 'sangat formal dan akademik',
            'santai': 'santai dan mudah dipahami',
            'ilmiah': 'ilmiah dan teknis',
            'singkat': 'lebih singkat dan padat',
        }
        style_desc = style_prompts.get(style, 'formal')

        prompt = f"""Parafrase teks berikut menjadi versi yang {style_desc}.
Pertahankan makna utama. Ubah struktur kalimat dan pilihan kata.
Berikan HANYA hasil parafrase tanpa penjelasan tambahan.

Teks asli:
{text}

Hasil parafrase:"""

        response = requests.post(
            'https://api.deepseek.com/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': 'deepseek-chat',
                'messages': [{'role': 'user', 'content': prompt}],
                'stream': False
            },
            timeout=30
        )

        if response.status_code == 200:
            result_data = response.json()
            paraphrased = result_data['choices'][0]['message']['content'].strip()
        else:
            paraphrased = f"[Simulasi Parafrase - {style}] {text}"

        # Simpan ke database
        result = ParaphraseResult.objects.create(
            user=request.user,
            original_text=text,
            paraphrased_text=paraphrased,
            style=style,
        )

        return JsonResponse({
            'success': True,
            'paraphrased': paraphrased,
            'id': result.id,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def api_plagiarisme(request):
    try:
        data = json.loads(request.body)
        text1 = data.get('text1', '').strip()
        text2 = data.get('text2', '').strip()

        if not text1 or not text2:
            return JsonResponse({'error': 'Kedua teks harus diisi.'}, status=400)

        similarity = compute_cosine_similarity(text1, text2)

        check = PlagiarismCheck.objects.create(
            user=request.user,
            text_1=text1,
            text_2=text2,
            similarity_percentage=similarity,
        )

        level = 'rendah' if similarity < 30 else 'sedang' if similarity < 70 else 'tinggi'
        color = '#22c55e' if similarity < 30 else '#f59e0b' if similarity < 70 else '#ef4444'

        return JsonResponse({
            'success': True,
            'similarity': round(similarity, 2),
            'level': level,
            'color': color,
            'id': check.id,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def api_upload(request):
    try:
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'error': 'File tidak ditemukan.'}, status=400)

        filename = uploaded_file.name
        ext = filename.rsplit('.', 1)[-1].lower()

        if ext not in ['txt', 'pdf']:
            return JsonResponse({'error': 'Format file tidak didukung. Gunakan .txt atau .pdf'}, status=400)

        extracted_text = ''

        if ext == 'txt':
            try:
                extracted_text = uploaded_file.read().decode('utf-8')
            except UnicodeDecodeError:
                extracted_text = uploaded_file.read().decode('latin-1')

        elif ext == 'pdf':
            try:
                import fitz  # PyMuPDF
                file_bytes = uploaded_file.read()
                doc = fitz.open(stream=file_bytes, filetype='pdf')
                for page in doc:
                    extracted_text += page.get_text()
                doc.close()
            except Exception:
                extracted_text = '[Gagal membaca PDF. Pastikan PyMuPDF terinstall.]'

        # Reset pointer sebelum simpan
        uploaded_file.seek(0)

        file_obj = UploadedFile.objects.create(
            user=request.user,
            file=uploaded_file,
            original_filename=filename,
            extracted_text=extracted_text[:5000],
        )

        return JsonResponse({
            'success': True,
            'filename': filename,
            'extracted_text': extracted_text[:500] + ('...' if len(extracted_text) > 500 else ''),
            'full_text': extracted_text[:3000],
            'id': file_obj.id,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_delete_history(request, pk, type):
    try:
        if type == 'parafrase':
            obj = get_object_or_404(ParaphraseResult, pk=pk, user=request.user)
        elif type == 'plagiarisme':
            obj = get_object_or_404(PlagiarismCheck, pk=pk, user=request.user)
        elif type == 'upload':
            obj = get_object_or_404(UploadedFile, pk=pk, user=request.user)
        else:
            return JsonResponse({'error': 'Tipe tidak valid'}, status=400)
        obj.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ─────────────────────────────────────────────
# HELPER: TF-IDF Cosine Similarity
# ─────────────────────────────────────────────

def tokenize(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text.split()


def compute_tfidf(corpus):
    N = len(corpus)
    tf_list = []
    df = Counter()

    for doc in corpus:
        tokens = tokenize(doc)
        tf = Counter(tokens)
        total = len(tokens) if tokens else 1
        tf_normalized = {k: v / total for k, v in tf.items()}
        tf_list.append(tf_normalized)
        df.update(set(tokens))

    vocab = list(df.keys())
    tfidf_list = []
    for tf in tf_list:
        tfidf = {}
        for word in vocab:
            t = tf.get(word, 0)
            idf = math.log((N + 1) / (df[word] + 1)) + 1
            tfidf[word] = t * idf
        tfidf_list.append(tfidf)

    return tfidf_list, vocab


def cosine_similarity(vec1, vec2, vocab):
    dot = sum(vec1.get(w, 0) * vec2.get(w, 0) for w in vocab)
    mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


def compute_cosine_similarity(text1, text2):
    corpus = [text1, text2]
    tfidf_list, vocab = compute_tfidf(corpus)
    sim = cosine_similarity(tfidf_list[0], tfidf_list[1], vocab)
    return sim * 100