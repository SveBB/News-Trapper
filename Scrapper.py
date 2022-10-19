"""Есть возможность описать скрэперы одним классом,
   но такое решение менее гибкое чем использование абстрактного класса"""

import re
import requests
from bs4 import BeautifulSoup as BS


class Scraper():
    def __init__(self, name, target, url, ):
        self.name = name
        self.target = target
        self.url = url
        self.dom_path = ''
        self.re_expression = ''
        self.titles = []

    def get_titles(self, dom_path):
        r = requests.get(self.url)
        html = BS(r.content, 'html.parser')
        items = html.select(dom_path)


        for i in items:
            title = {'text': '', 'url': ''}
            title['text'] = i.text
            title['url'] = i.get('href')
            self.titles.append(title)
        print(items)
    def clear_titles(self, re_expression):
        for title in self.titles:
            title['text'] = re.findall(r''.join(re_expression), title['text'])[0]
            title['url'] = self.target+title['url']
            print(title['text'])
            print(title['url'])

lenta = Scraper('lenta', 'https://lenta.ru', 'https://lenta.ru/parts/news/')
lenta.get_titles('.parts-page__item > a')
lenta.clear_titles('^\D+')


riaeconomy = Scraper('rio economy', 'https://ria.ru', 'https://ria.ru/economy/')
riaeconomy.get_titles('.cell-list__list > .m-no-image > a')
riaeconomy.clear_titles('')
