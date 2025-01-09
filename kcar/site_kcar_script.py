from kcar import site_kcar, site_kcar_dop
from utils import translation


async def run_parser():
    await site_kcar.main()

    await site_kcar_dop.process_cars()
    # await translation.update_database(site_kcar.TimeDealCar, batch_size=10, delay=3, max_concurrent_requests=5)


if __name__ == "__main__":
    site_kcar.main_run()

    site_kcar_dop.main()
