from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from datetime import timedelta
import threading
from django.core.mail import send_mail
from django.conf import settings

def delete_old_chats():

    from .models import ChatHistory
    
    cutoff_date = timezone.now() - timedelta(days=30)
    
    old_chats = ChatHistory.objects.filter(created_at__lte=cutoff_date)
    count = old_chats.count()
    old_chats.delete()
    
    print(f"Cleanup Task: Deleted {count} old chat records.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_old_chats, 'interval', hours=24)
    scheduler.start()
    print("Background Scheduler Started() !")
    
def send_welcome_email_task(user_email, username):
    subject = 'Welcome to the AI Chatbot!'
    message = f'Hi {username},\n\nThank you for registering. Your account has been successfully created.\n\nBest,\nThe AI Team'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email]

    try:
        send_mail(subject, message, email_from, recipient_list)
        print(f"📧 Email Task: Sent welcome email to {user_email}")
    except Exception as e:
        print(f"Email Task Failed: {e}")

def run_email_background(user_email, username):
    thread = threading.Thread(target=send_welcome_email_task, args=(user_email, username))
    thread.start()