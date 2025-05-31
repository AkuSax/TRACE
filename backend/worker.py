import time
from celery import Celery

# Create a Celery application instance
celery_app = Celery(
    'worker',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# Optional: Configure Celery for better performance and resource management
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task
def add_numbers(x, y):
    """
    A simple test task that adds two numbers and simulates a delay.
    """
    time.sleep(5)  # Simulate a 5-second long-running task
    return x + y