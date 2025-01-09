from autohub import site_autohub
from utils import translation


async def run_parser():
    await site_autohub.process_cars()
    # await translation.update_database(site_autohub.TimeDealCar, batch_size=10, delay=3, max_concurrent_requests=5)


if __name__ == "__main__":
    site_autohub.main()
