from django.urls import path
from .views import (
    PromptListView, PromptDetailView, GenerateContentView,
    ImagePromptListView, ImagePromptDetailView
)

urlpatterns = [
    # Text prompts
    path('', PromptListView.as_view(), name='prompt-list'),
    path('<int:pk>/', PromptDetailView.as_view(), name='prompt-detail'),
    path('generate/', GenerateContentView.as_view(), name='generate-content'),
    
    # Image prompts
    path('image/', ImagePromptListView.as_view(), name='image-prompt-list'),
    path('image/<int:pk>/', ImagePromptDetailView.as_view(), name='image-prompt-detail'),
]
