"""Скрапер для lenta.ru"""
import re
from scraper_abstract import Scraper

class Lenta (Scraper):
    """Класс скрапера для lenta.ru"""
    def parse_html(self):
        """Переопределенный метод парсинга"""
        items = self.html.select('.parts-page__item > a')
        for item in items:
            title = {'text': '', 'source': '', 'url': ''}
            re_expression = '^\D+'
            title['text'] = re.findall(r''.join(re_expression), item.text)[0]
            title['source'] = self.target
            if item.get('href')[:4] == 'http':
                title['url'] = item.get('href')
            else:
                title['url'] = self.target + item.get('href')
            if title['url'] != "/parts/news/2/":
                self.titles.append(title)

        return self.titles

if __name__ == '__main__':
    obj = Lenta('https://lenta.ru', 'https://lenta.ru/parts/news/')
    obj.parse_html()
    obj.write_info()
