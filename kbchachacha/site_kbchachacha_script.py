from kbchachacha import site_kbchachacha, site_kbchachacha_dop
import time
from utils.log import logger

if __name__ == "__main__":
    start = start_time = time.time()
    logger.info(f"Начало сбора данных для kbchachacha")

    site_kbchachacha.main()

    site_kbchachacha_dop.main()

    elapsed_time = time.time() - start_time
    logger.info(f"Конец сбора данных для kbchachacha: время сбора данных =  {elapsed_time:.2f} сукунд")
