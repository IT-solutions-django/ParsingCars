import aiohttp
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.log import logger

DATABASE_URL = "sqlite:///cars_2.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

API_KEY = "AQVNzE4LmRfVyyBTGMQs73okTV-U-LQX0jT84hsr"
URL = "https://translate.api.cloud.yandex.net/translate/v2/translate"


def create_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {API_KEY}"
    }


async def translate_text(session, text, target_language="en", source_language="ko"):
    data = {
        "targetLanguageCode": target_language,
        "texts": [text],
        "sourceLanguageCode": source_language
    }

    async with session.post(URL, json=data, headers=create_headers()) as response:
        if response.status == 200:
            result = await response.json()
            return result["translations"][0]["text"]
        else:
            logger.error(f"Ошибка: {response.status}, {await response.text()}")
            return None


async def process_record(record, session, semaphore, color_param):
    is_translation = False
    async with semaphore:
        if record.car_mark and not record.car_mark.isascii():
            translated_mark = await translate_text(session, record.car_mark, target_language="en", source_language="ko")
            if translated_mark:
                record.car_mark = translated_mark

            is_translation = True

        if record.car_model and not record.car_model.isascii():
            translated_model = await translate_text(session, record.car_model, target_language="en",
                                                    source_language="ko")
            if translated_model:
                record.car_model = translated_model

            is_translation = True

        if not color_param:
            if record.color and not record.color.isascii():  # Поменять проверку на русский
                translated_color = await translate_text(session, record.color, target_language="ru",
                                                        source_language="ko")
                if translated_color:
                    record.color = translated_color

                is_translation = True
        else:
            if record.car_color and not record.car_color.isascii():  # Поменять проверку на русский
                translated_color = await translate_text(session, record.car_color, target_language="ru",
                                                        source_language="ko")
                if translated_color:
                    record.car_color = translated_color

                is_translation = True

        if is_translation:
            await asyncio.sleep(1)


async def update_database(models, batch_size=10, delay=5, max_concurrent_requests=5, color_param=False):
    semaphore = asyncio.Semaphore(max_concurrent_requests)
    session = Session()
    records = session.query(models).all()

    async with aiohttp.ClientSession() as http_session:
        tasks = []

        for idx, record in enumerate(records, start=1):
            tasks.append(process_record(record, http_session, semaphore, color_param))

            if idx % batch_size == 0:
                await asyncio.gather(*tasks)
                session.commit()
                tasks = []
                await asyncio.sleep(delay)

        if tasks:
            await asyncio.gather(*tasks)
        session.commit()
    session.close()
