"""Абстрактный класс описывающий шаблон для других скраперов"""
import json
import os
import sys
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup as BS


class Scraper (ABC):
    """Абстрктный класс для сборщиков информации"""
    def __init__(self, target, url):

        __html_example = """<html><head><title>The Dormouse's story</title></head>
                        <body>
                        <p class="title"><b>The Dormouse's story</b></p>
                        <a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>"""

        self.target = target
        self.url = url
        try:
            self.html = BS(requests.get(self.url).content, 'html.parser')
            print("GOOD RESPONSE:" + self.target)
        except Exception:
            self.html = BS(__html_example,'html.parser')
            print("ERROR:" + self.target + " BAD CONNECTION")
        self.titles  = []
    def write_info(self):
        """Запись полученных заголовков в общий файл"""
        if os.path.exists('temp\collected_data.json'):
            with open("temp\collected_data.json", "r+", encoding='utf-8') as file:
                data = json.load(file)
                data += self.titles
                file.seek(0)
                json.dump(data, file, ensure_ascii=False)
            file.close()
        else:
            with open('temp\collected_data.json', 'w', encoding='utf-8') as file:
                json.dump(self.titles, file, ensure_ascii=False)
            file.close()

    @abstractmethod
    def parse_html(self):
        """Абстрактный метод парсинга полученного html,
           индивидаульно для структуры кажждого таргета.
           Метод должен заполнить self.titles записями
           формата {'text': '', 'source': '', 'url': ''}"""


if __name__ == '__main__':
    print("RUN: ")
