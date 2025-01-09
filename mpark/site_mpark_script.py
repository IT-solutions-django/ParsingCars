from mpark import site_mpark, site_mpark_dop
from utils import translation


async def run_parser():
    await site_mpark.main()

    await site_mpark_dop.main()
    # await translation.update_database(site_mpark.TimeDealCar, batch_size=10, delay=3, max_concurrent_requests=5,
    #                                   color_param=True)


if __name__ == "__main__":
    site_mpark.main_run()

    site_mpark_dop.main_run()
