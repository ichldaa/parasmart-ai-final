from django.db import models
from django.contrib.auth.models import User


class ParaphraseResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paraphrases')
    original_text = models.TextField()
    paraphrased_text = models.TextField()
    style = models.CharField(max_length=50, default='formal')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Parafrase by {self.user.username} - {self.created_at.strftime('%d/%m/%Y')}"

    def short_text(self):
        return self.original_text[:60] + '...' if len(self.original_text) > 60 else self.original_text


class PlagiarismCheck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plagiarism_checks')
    text_1 = models.TextField()
    text_2 = models.TextField()
    similarity_percentage = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Plagiarisme by {self.user.username} - {self.similarity_percentage:.1f}%"


class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    file = models.FileField(upload_to='uploads/')
    original_filename = models.CharField(max_length=255)
    extracted_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.original_filename} by {self.user.username}"
