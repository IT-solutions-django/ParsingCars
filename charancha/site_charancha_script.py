from charancha import site_charancha, site_charancha_dop


async def run_parser():
    await site_charancha.process_cars()

    await site_charancha_dop.process_cars()


if __name__ == "__main__":
    site_charancha.main()

    site_charancha_dop.main()
