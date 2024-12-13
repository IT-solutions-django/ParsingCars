from bobaedream import site_bobaedream, site_bobaedream_dop


async def run_parser():
    await site_bobaedream.process_cars()
    await site_bobaedream_dop.process_cars()


if __name__ == "__main__":
    site_bobaedream.main()
    site_bobaedream_dop.main()
