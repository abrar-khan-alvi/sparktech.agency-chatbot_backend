from django.apps import AppConfig

class ChatbotApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot_api'

    def ready(self):
        from .tasks import start_scheduler
        try:
            start_scheduler()
        except Exception as e:
            print(f"Scheduler failed to start: {e}")