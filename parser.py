import sqlite3

import requests
import json
from bs4 import BeautifulSoup
import urllib3
from sqlighter1 import SQLighter1

urllib3.disable_warnings()

db1 = SQLighter1('db_bars.db')


def get_bars():
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    }
    url = 'https://www.restoclub.ru/msk/search?expertChoice=false&types%5B%5D=3&types%5B%5D=16&types%5B%5D=7&types%5B%5D=4&types%5B%5D=1&types%5B%5D=17&types%5B%5D=22'

    response = requests.get(url=url, headers=headers, verify=False)

    soup = BeautifulSoup(response.text, "lxml")

    pages_count = int(soup.find("nav", class_='pagination').find_all("a")[-2].text)

    bars_data = {}

    for page in range(1, pages_count + 1):
        url = f'https://www.restoclub.ru/msk/search/{page}?expertChoice=false&types%5B%5D=3&types%5B%5D=16&types%5B%5D=7&types%5B%5D=4&types%5B%5D=1&types%5B%5D=17&types%5B%5D=22'
        response = requests.get(url=url, headers=headers, verify=False)
        soup = BeautifulSoup(response.text, "lxml")

        bar_items = soup.find("ul", 'page-search__list').find_all("li", class_='page-search__item')

        for bi in bar_items:
            bar_title = bi.find("div", class_='search-place-card__title').text.strip()
            bar_description = bi.find("div", class_='search-place-card__about').text.strip()
            if str(type(bi.find("li", class_='search-place-card__info-item'))) == "<class 'bs4.element.Tag'>":
                if str(type(bi.find("li", class_='search-place-card__info-item').find(
                        "span"))) == "<class 'bs4.element.Tag'>":
                    bar_metro = bi.find("li", class_='search-place-card__info-item').find("span").text.strip()
                else:
                    bar_metro = 'Метро не указано'
            bar_url0 = bi.find("a")
            bar_url = f'https://www.restoclub.ru{bar_url0.get("href")}'
            # print(f"{bar_title} | {bar_description} | {bar_url} | {bar_metro}")

            db1.add_bar(bar_title=bar_title, bar_description=bar_description, bar_metro=bar_metro, bar_url=bar_url,
                        bar_users='')

            bars_data[bar_title] = (
                {
                    'bar_title': bar_title,
                    'bar_description': bar_description,
                    'bar_url': bar_url,
                    'bar_metro': bar_metro
                }
            )

        with open("bars_dict.json", "w", encoding='utf-8') as file:
            json.dump(bars_data, file, indent=4, ensure_ascii=False)


def main():
    get_bars()


if __name__ == '__main__':
    main()

'''with open('keys.json', encoding='utf-8') as file:
    data = json.load(fh)
'''
