from autohub import site_autohub


async def run_parser():
    await site_autohub.process_cars()


if __name__ == "__main__":
    site_autohub.main()
