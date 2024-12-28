import aiohttp
import asyncio
from utils.log import logger
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, select
import pytz
from datetime import datetime

Base = declarative_base()

novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")


def get_novosibirsk_time():
    return datetime.now(novosibirsk_tz)


class AutoInside(Base):
    __tablename__ = "site_autoinside_cars"

    id = Column(Integer, primary_key=True, index=True)
    id_car = Column(String)
    url_car = Column(String)
    car_mark = Column(String)
    car_model = Column(String)
    car_type = Column(String)
    year = Column(Integer)
    car_fuel = Column(String)
    transmission = Column(String)
    engine_capacity = Column(Integer)
    color = Column(String)
    price = Column(String)
    millage = Column(Integer)
    main_image = Column(String)
    images = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False, default=get_novosibirsk_time)
    updated_at = Column(DateTime(timezone=True), onupdate=get_novosibirsk_time, nullable=False,
                        default=get_novosibirsk_time)


async def fetch_page(session, page_number, semaphore):
    url = "https://www.autoinside.co.kr/display/bu/display_bu_used_car_list_ajax.do"
    payload = {
        "i_sReturnUrl": "/display/bu/display_bu_used_car_list.do",
        "i_sReturnParam": "",
        "i_iNowPageNo": page_number,
        "i_iTotalPageCnt": 26,
        "i_sFlagAction": "HC",
        "i_sIsApp": "N",
        "i_sFlagSearch": "REG",
        "i_sSchCar": "",
        "i_sCarCategoryAll": "ALL",
        "i_sMnfcCd": "",
        "i_sBrandCd": "",
        "i_sModelCd": "",
        "i_sFlagAllSelCar": "ALL",
        "i_arrFlagSelCar": "DPT200",
        "i_arrFlagSelCar": "DPT300",
        "i_arrFlagSelCar": "DPT600",
        "i_arrFlagSelCar": "DPT500",
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
    }

    async with semaphore:
        try:
            async with session.post(url, data=payload, headers=headers, timeout=100) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Ошибка запроса для страницы {page_number}, status: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Ошибка запроса для страницы {page_number}: {e}")
            return None


async def save_to_db(engine, car_data):
    try:
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            async with session.begin():
                objects = car_data.get("object", None)
                if objects:
                    list_cars = objects.get("list", [])
                    car_ids = [car.get("v_carcd") for car in list_cars]

                    existing_ids = await session.execute(
                        select(AutoInside.id_car).where(AutoInside.id_car.in_(car_ids))
                    )
                    existing_ids = set(existing_ids.scalars())

                    for car in list_cars:
                        id_car = car.get("v_carcd")

                        if id_car not in existing_ids:
                            main_image = car.get("v_imgnm", None)
                            if main_image:
                                main_image = images = f"https://www.autoinside.co.kr/shCardImg/{main_image}"
                            else:
                                images = None

                            url_car = f"https://www.autoinside.co.kr/display/bu/display_bu_used_ah_car_view.do?XC_VCL_CD={id_car}&i_sCarCd={id_car}"

                            new_car = AutoInside(
                                id_car=id_car,
                                url_car=url_car,
                                car_mark=car.get("xc_mkco_nm", None),
                                car_model=car.get("xc_vcl_brnd_nm", None),
                                car_type=car.get("xc_vctp_nm", None),
                                year=car.get("v_pyy_yy", None),
                                car_fuel=car.get("v_fuelcd_nm", None),
                                transmission=car.get("v_gboxcd_nm", None),
                                engine_capacity=car.get("n_exhu_qty", None),
                                color=car.get("v_clrcd_nm", None),
                                price=car.get("n_new_vcl_prc", None),
                                millage=car.get("n_dvml", None),
                                main_image=main_image,
                                images=images
                            )
                            session.add(new_car)
    except Exception as e:
        logger.error(f"Ошибка сохранения записи в БД: {e}")


async def process_page(http_session, engine, page_number, semaphore):
    data = await fetch_page(http_session, page_number, semaphore)
    if data is not None:
        await save_to_db(engine, data)
    else:
        return None


async def main():
    database_url = "sqlite+aiosqlite:///cars_2.db"
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    semaphore = asyncio.Semaphore(10)

    async with aiohttp.ClientSession() as http_session:
        tasks = [
            process_page(http_session, engine, page_number, semaphore)
            for page_number in range(1, 28)
        ]
        await asyncio.gather(*tasks)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
