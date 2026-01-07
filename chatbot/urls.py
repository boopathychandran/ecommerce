from django.urls import path
from . import views

urlpatterns = [
    path('api/chat/', views.chat_response, name='chat_response'),
    # Compatibility endpoint used by frontend JS (fetch('/chatbot/response/'))
    path('response/', views.chat_response, name='chat_response_response'),
]
