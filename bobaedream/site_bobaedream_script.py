from bobaedream import site_bobaedream, site_bobaedream_dop
from utils import translation


async def run_parser():
    await site_bobaedream.process_cars()
    await site_bobaedream_dop.process_cars()
    # await translation.update_database(site_bobaedream.TimeDealCar, batch_size=10, delay=3, max_concurrent_requests=5)


if __name__ == "__main__":
    site_bobaedream.main()
    site_bobaedream_dop.main()
