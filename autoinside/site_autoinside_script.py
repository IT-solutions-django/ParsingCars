from autoinside import site_autoinside
from utils import translation


async def run_parser():
    await site_autoinside.main()
    # await translation.update_database(site_autoinside.AutoInside, batch_size=10, delay=3, max_concurrent_requests=5)


if __name__ == "__main__":
    site_autoinside.main()
