from django.urls import path
from .views import RegisterView, ChatView, ChatHistoryView 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='auth_register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Did you miss these lines?
    path('chat/', ChatView.as_view(), name='chat'),
    path('chat-history/', ChatHistoryView.as_view(), name='chat_history'),
]