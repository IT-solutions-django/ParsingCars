import requests
from utils.log import logger
import time
import aiohttp
import asyncio
import json


async def fetch_page_data(session, page, headers, retries=3, backoff=2):
    url = f"https://www.bobaedream.co.kr/mycar/proc/ajax_contents.php?page={page}&view_size=10"
    for attempt in range(retries):
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=50)) as response:
                if response.status == 200:
                    content = await response.text()

                    try:
                        data = json.loads(content)
                        return data
                    except json.JSONDecodeError:
                        logger.error(f"Ошибка декодирования JSON. Ответ сервера:\n{content}")
                        return None
                else:
                    logger.error(f"Неожиданный статус ответа: {response.status}, URL: {url}")
                    return None
        except Exception as e:
            logger.error(
                f"Ошибка при выполнении запроса к API для страницы {page}, попытка {attempt + 1}/{retries}: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(backoff)
                backoff *= 2
            else:
                logger.error(f"Запрос для страницы {page} провалился окончательно.")
                return None


async def fetch_car_details(id_car):
    url = f"https://www.bobaedream.co.kr/cyber/CyberCar_view.php?no={id_car}&gubun=I"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                response.raise_for_status()
                return await response.text()
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка при выполнении запроса к API для {id_car}: {e}")
        return None


def fetch_car_details_json(url, id_car):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к API для {id_car}: {e}")
        return None


def fetch_post_car_details_json(url, id_car, data):
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к API для {id_car}: {e}")
        return None


def fetch_post_page_data(url, data, page, retries=3, backoff=2):
    for attempt in range(retries):
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при выполнении запроса к API для page {page}, попытка {attempt + 1}/{retries}: {e}")
            if attempt < retries - 1:
                time.sleep(backoff)
                backoff *= 2
            else:
                logger.error(f"Запрос к API для page {page} окончательно провалился после {retries} попыток.")
                return None
