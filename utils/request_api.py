import requests
from utils.log import logger
import time
import aiohttp
import asyncio
import json
import random

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.121 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.119 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'
]


async def fetch_page_data(session, page, headers, retries=3, backoff=2):
    random_user_agent = random.choice(user_agents)
    headers['User-Agent'] = random_user_agent
    url = f"https://www.bobaedream.co.kr/mycar/proc/ajax_contents.php?page={page}&view_size=70"
    for attempt in range(retries):
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=180)) as response:
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
    random_user_agent = random.choice(user_agents)
    headers = {
        'User-Agent': random_user_agent,
        'Referer': 'https://www.bobaedream.co.kr/cyber/CyberCar.php?sel_m_gubun=ALL&order=S11&view_size=70',
        'Cookie': '_ga=GA1.1.1209283205.1732503816; _ga_F5YV62DJXL=GS1.1.1735389609.9.0.1735389611.0.0.0',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'DNT': '1'
    }
    url = f"https://www.bobaedream.co.kr/cyber/CyberCar_view.php?no={id_car}&gubun=I"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=180), headers=headers) as response:
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
