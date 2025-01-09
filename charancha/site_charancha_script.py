from charancha import site_charancha, site_charancha_dop
from utils import translation


async def run_parser():
    await site_charancha.process_cars()

    await site_charancha_dop.process_cars()
    # await translation.update_database(site_charancha.TimeDealCar, batch_size=10, delay=3, max_concurrent_requests=5)


if __name__ == "__main__":
    site_charancha.main()

    site_charancha_dop.main()
