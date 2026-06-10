from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Parafrase
    path('parafrase/', views.parafrase_view, name='parafrase'),
    path('api/parafrase/', views.api_parafrase, name='api_parafrase'),

    # Plagiarisme
    path('plagiarisme/', views.plagiarisme_view, name='plagiarisme'),
    path('api/plagiarisme/', views.api_plagiarisme, name='api_plagiarisme'),

    # Upload
    path('upload/', views.upload_view, name='upload'),
    path('api/upload/', views.api_upload, name='api_upload'),

    # History
    path('history/', views.history_view, name='history'),
    path('api/history/delete/<int:pk>/<str:type>/', views.api_delete_history, name='api_delete_history'),

    path('profile/', views.profile_view, name='profile'),
]
