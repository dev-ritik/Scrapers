import random
import sys
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from raw_data.wb_data import PARTY_2021_CONVERSION, DELAYED_CONSTITUENCIES
from scraper.base_scraper import BaseScraper


class ECScraper(BaseScraper):

    def __init__(self):
        super(ECScraper, self).__init__()
        self.source = "EC"

        self.session = requests.Session()

        retry = Retry(connect=5, backoff_factor=0.2)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _attempt(self, constituency: int) -> (int, Optional[bytes]):
        url = f"https://results.eci.gov.in/Result2021/ConstituencywiseS25{constituency}.htm?ac={constituency}"
        rand = random.uniform(0, 1)
        time.sleep(2.2 + rand * 1)

        user_agents = ['Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',
                       'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 '
                       'Safari/537.36',
                       'Mozilla/5.0 (Windows NT 5.1; rv:9.0.1) Gecko/20100101 Firefox/9.0.1',
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/60.0.3112.113 Safari/537.36']

        headers = {
            'authority': 'results.eci.gov.in',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            'sec-ch-ua-mobile': '?0',
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': user_agents[int(rand * 4) % 4],
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://results.eci.gov.in/Result2021/ConstituencywiseS25{constituency}.htm?ac={constituency}',
            'accept-language': 'en-US,en;q=0.9,hi-IN;q=0.8,hi;q=0.7,he-IL;q=0.6,he;q=0.5'
        }

        payload = {}
        response = self.session.get(url, headers=headers, data=payload, timeout=30)

        if response.status_code != 200:
            print("fatal error", file=sys.stderr)
            return -1, None
        if response.text.__contains__('Result Not Found'):
            return 0, None
        else:
            return 1, response.content

    @staticmethod
    def _parse_html(content: Optional[bytes]) -> {}:
        content = BeautifulSoup(content, "html.parser")
        main_table = \
            content.find_all('table')[0].find('tbody').find_all('tr', recursive=False)[2].find('td').find_all('table',
                                                                                                              recursive=False)[
                2]
        table = main_table.find('tbody').find('tr').find('td').find('table').find('tbody').find('tr').find('td').find(
            'div').find('table').find('tbody')
        candidates = {}
        for row in table.find_all('tr', recursive=False)[3:-1]:
            cells = row.find_all('td', recursive=False)
            candidates[PARTY_2021_CONVERSION[cells[2].text]] = int(cells[5].text)
        return candidates

    def get_constituency_party_wise_votes(self, constituency_index: int) -> (int, {}):
        if constituency_index in range(1, 295) and constituency_index not in [56, 58]:
            status, res = self._attempt(constituency_index)
            if status == 1:
                asd = ECScraper._parse_html(res)
                print(constituency_index, asd)
                return 1, asd
        return -1, {}