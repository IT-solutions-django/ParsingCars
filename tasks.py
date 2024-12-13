import asyncio
from celery import Celery
from autohub.site_autohub_script import run_parser as parse_1
from bobaedream.site_bobaedream_script import run_parser as parse_2
from charancha.site_charancha_script import run_parser as parse_3
from kcar.site_kcar_script import run_parser as parse_4
from mpark.site_mpark_script import run_parser as parse_5
from utils.log import logger
from celery.schedules import crontab

app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')


async def run_parsers():
    logger.info("Задачи запустились")
    tasks = [
        parse_1(),
        parse_2(),
        parse_3(),
        parse_4(),
        parse_5()
    ]
    results = await asyncio.gather(*tasks)
    logger.info(f"Результаты парсеров: {results}")
    return results


@app.task
def run_all_parsers():
    logger.info("Запуск задачи Celery 'run_all_parsers'")

    result = asyncio.run(run_parsers())
    return result


app.conf.beat_schedule = {
    'run-every-day-at-9am': {
        'task': 'tasks.run_all_parsers',
        'schedule': crontab(hour=9, minute=0),
    },
}
app.conf.timezone = 'Asia/Novosibirsk'
