import asyncio
from celery import Celery
from autohub.site_autohub_script import run_parser as parse_1
from bobaedream.site_bobaedream_script import run_parser as parse_2
from charancha.site_charancha_script import run_parser as parse_3
from kcar.site_kcar_script import run_parser as parse_4
from mpark.site_mpark_script import run_parser as parse_5
from utils.log import logger
from celery.schedules import crontab
from asgiref.sync import async_to_sync

app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')


async def run_parsers():
    logger.info("Задачи запустились")

    await parse_1()
    await parse_2()
    await parse_3()
    await parse_4()
    await parse_5()

    logger.info(f"Задачи завершились")


@app.task
def run_all_parsers():
    logger.info("Запуск задачи Celery 'run_all_parsers'")

    result = async_to_sync(run_parsers)()
    return result


app.conf.beat_schedule = {
    'run-every-day-at-19am': {
        'task': 'tasks.run_all_parsers',
        'schedule': crontab(hour=19, minute=0),
    },
}
app.conf.timezone = 'Asia/Novosibirsk'
