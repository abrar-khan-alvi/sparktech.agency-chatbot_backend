from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, ChatHistorySerializer
from .models import ChatHistory
from .utils import generate_rag_response
from .tasks import run_email_background  # <-- This import works now!

# 1. Registration View (With Email)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # Trigger Background Email
        if user.email:
            run_email_background(user.email, user.username)

# 2. Chat View (The Brain)
class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_message = request.data.get('message')
        if not user_message:
            return Response({"error": "Message is required"}, status=400)

        ai_reply = generate_rag_response(user_message)

        ChatHistory.objects.create(
            user=request.user,
            user_message=user_message,
            ai_response=ai_reply
        )

        return Response({
            "user_message": user_message,
            "ai_response": ai_reply
        })

# 3. History View (The Memory)
class ChatHistoryView(generics.ListAPIView):
    serializer_class = ChatHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatHistory.objects.filter(user=self.request.user).order_by('-created_at')