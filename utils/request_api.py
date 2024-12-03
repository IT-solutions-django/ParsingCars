import requests
from utils.log import logger


def fetch_page_data(page, headers):
    url = f"https://www.bobaedream.co.kr/mycar/proc/ajax_contents.php?sel_m_gubun=ALL&page={page}&order=S11&view_size=70&dummy=1732848489318"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к API для page {page}: {e}")
        return None


def fetch_car_details(id_car):
    url = f"https://www.bobaedream.co.kr/cyber/CyberCar_view.php?no={id_car}&gubun=I"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
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
