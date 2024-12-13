from kcar import site_kcar, site_kcar_dop


async def run_parser():
    await site_kcar.main()

    await site_kcar_dop.process_cars()


if __name__ == "__main__":
    site_kcar.main_run()

    site_kcar_dop.main()
