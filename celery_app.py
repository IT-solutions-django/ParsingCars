from celery import Celery
from celery.schedules import crontab

app = Celery(
    'tasks',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

# app.conf.beat_schedule = {
#     'daily-parsing-task': {
#         'task': 'tasks.run_all_parsers',
#         'schedule': crontab(hour=0, minute=0),
#     },
# }
#
# app.conf.timezone = 'Asia/Novosibirsk'
