from datetime import datetime
import schedule
import time
import logging

from dates_finder import DatesFinder
from mailer import send_error_mail
from dates_finder_logger import init_logger
from config import GLOBAL_CONFIG

logger = init_logger()


def job():
    logger.log(logging.INFO, "----- Launching DatesFinder job -----")
    dates_finder = DatesFinder()
    found_dates = dates_finder.find_available_dates()
    if found_dates and GLOBAL_CONFIG['main_schedule']['break_when_found']:
        logger.log(logging.INFO, "Found dates, closing the app")
        exit(0)


schedule.every(1).to(2).hours.do(job)
# schedule.every(3).to(6).seconds.do(job)  # debug

if __name__ == '__main__':
    try:
        while datetime.now() < datetime(2022, 8, 5):
            schedule.run_pending()
            time.sleep(60 * 15)
        logger.log(logging.INFO, "----- Scheduler finished -----")
    except:
        logger.log(logging.ERROR, "Error in main scheduler")
        send_error_mail()
        raise
