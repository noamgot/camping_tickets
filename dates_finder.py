import time
import logging
import random
from typing import List, Tuple, Union
from datetime import datetime, date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from dates_finder_logger import init_logger
from mailer import send_mail, receivers
from config import GLOBAL_CONFIG

dates_finder_config = GLOBAL_CONFIG['dates_finder']

class DatesFinder:

    def __init__(self):
        
        self.driver = self._init_driver()
        self.possible_dates = self._reformat_possible_dates(dates_finder_config['possible_dates'])
        self.url_template = self._init_url_template(dates_finder_config)
        self.logger = init_logger()
        self.logger.info("DatesFinder initialized")
    
    @staticmethod
    def _init_driver() -> webdriver.Chrome:
        """
        Initialize selenium webdriver

        Returns:
            webdriver.Chrome: selenium chrome driver
        """
        options = Options()
        options.add_argument('--headless')
        # modify user-agent to fool the website to think we are a real browser
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)  # wait up to 10 seconds in case loading takes too long
        return driver
    
    @staticmethod
    def _init_url_template(dates_finder_config: dict) -> str:
        """
        Initialize the url template for the dates finder

        Args:
            dates_finder_config (dict): the dates finder config dict

        Raises:
            ValueError: if the number of participants is less than the minimum allowed

        Returns:
            str: final url template
        """
        base_url = 'https://secure-hotels.net/INPA/BE_Results.aspx?lang=heb&hotel=9&In={}&Out={}&Rooms=1'
        for config_key, min_val, url_key in [('num_adults', 1, 'Ad1'), ('num_children', 0, 'Ch1'), ('num_infants', 0, 'Inf1')]:
            val = dates_finder_config[config_key]
            if val < min_val:
                raise ValueError(f'{config_key} must be >= {min_val}')
            if val > 0:
                base_url += '&' + url_key + '=' + str(val)
        return base_url
        
        
    @staticmethod
    def _reformat_possible_dates(possible_dates: List[Tuple[Union[date, str], Union[date, str]]]) -> List[Tuple[str, str]]:
        """
        Modify possible_dates such that it contains string tuples
        
        Args:
            possible_dates (List[Tuple[Union[date, str], Union[date, str]]]): list of possible dates as tuples

        Returns:
            List[Tuple[str, str]]: list of possible dates as string tuples
        """
        possible_dates_reformatted = []
        for in_date, out_date in possible_dates:
            if isinstance(in_date, date):
                in_date_reformat = str(in_date)
            if isinstance(out_date, date):
                out_date_reformat = str(out_date)
            possible_dates_reformatted.append((in_date_reformat, out_date_reformat))
        return possible_dates_reformatted

    @staticmethod
    def reformat_date(date: str) -> str:
        return datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')

    def available_dates_to_txt(self, available_dates: List[Tuple[str, str]]) -> str:
        """
        Generate a text message with the available dates

        Args:
            available_dates (List[Tuple[str, str]]): list of available dates as string tuples

        Returns:
            str: text message with the available dates
        """
        available_dates_strs = []
        for in_date, out_date in available_dates:
            available_dates_strs.append(self.reformat_date(in_date) + ' - ' + self.reformat_date(out_date))
            available_dates_strs.append(self.url_template.format(in_date, out_date))
        ad = '\n'.join(available_dates_strs)

        text = 'שלום!\n' \
               'התאריכים הבאים פנויים להזמנה בחורשת טל:\n' \
               '{}\n' \
               'להתראות!'.format(ad)
        return text

    def find_available_dates(self) -> bool:
        """
        The main function of the class. Finds available dates and sends them to the users

        Returns:
            bool: True if there are available dates, False otherwise
        """
        available_dates = []
        first_iter = True

        for in_date, out_date in self.possible_dates:
            if not first_iter:
                time.sleep(random.random() * 4 + 1)
            first_iter = False
            url = self.url_template.format(in_date, out_date)
            in_date_reformat = self.reformat_date(in_date)
            out_date_reformat = self.reformat_date(out_date)
            self.logger.log(logging.DEBUG, f'Testing url: {url}')
            self.driver.get(url)
            try:
                self.driver.find_element(By.CLASS_NAME, 'rooms-list-title')
                self.logger.log(logging.INFO,"*** Found rooms for {} - {}! ***".format(in_date_reformat, out_date_reformat))
                available_dates.append((in_date, out_date))
            except NoSuchElementException:
                # uncomment for debugging
                # driver.get_screenshot_as_file(f"{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}_screenshot.png")
                self.logger.log(logging.INFO, "No rooms for {} - {}".format(in_date_reformat, out_date_reformat))

        if available_dates:
            self.logger.log(logging.INFO, f"Sending all available dates to {receivers}")
            available_dates_txt = self.available_dates_to_txt(available_dates)
            send_mail(available_dates_txt)
            self.logger.log(logging.INFO, "Done!")
            return True
        return False


if __name__ == '__main__':
    df = DatesFinder()
    df.find_available_dates()
