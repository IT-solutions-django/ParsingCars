from mpark import site_mpark, site_mpark_dop


async def run_parser():
    await site_mpark.main()

    await site_mpark_dop.main()


if __name__ == "__main__":
    site_mpark.main_run()

    site_mpark_dop.main_run()
