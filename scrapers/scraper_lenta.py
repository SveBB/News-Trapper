"""Скрапер для lenta.ru"""
import re
from scraper_abstract import Scraper

class Lenta (Scraper):
    """Класс скрапера для lenta.ru"""
    def parse_html(self):
        """Переопределенный метод парсинга"""
        items = self.html.select('.parts-page__item > a')
        for item in items:
            title = {'name': '', 'text': '', 'source': '', 'url': ''}
            title['name'] = self.name
            re_expression = '^\D+'
            try:
                title['text'] = re.findall(r''.join(re_expression), item.text)[0]
            except Exception:
                title['text'] = item.text
            title['source'] = self.target
            if item.get('href')[:4] == 'http':
                title['url'] = item.get('href')
            else:
                title['url'] = self.target + item.get('href')
            if title['url'] != "/parts/news/2/" and title['text'] != "Показать ещеЗагрузка":
                self.titles.append(title)

        return self.titles

if __name__ == '__main__':
    obj = Lenta('Lenta.ru', 'https://lenta.ru', 'https://lenta.ru/parts/news/')
    obj.parse_html()
    obj.write_info()
