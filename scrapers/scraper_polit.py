"""Скрапер для polit.ru"""
from scraper_abstract import Scraper

class Polit (Scraper):
    """Класс скрапера для lenta.ru"""
    def parse_html(self):
        """Переопределенный метод парсинга"""
        items = self.html.select('.news-full.stop > .title > a')
        for item in items:
            title = {'text': '', 'source': '', 'url': ''}
            title['text'] = item.text
            title['source'] = self.target
            title['url'] = self.target + item.get('href')
            self.titles.append(title)

        return self.titles


if __name__ == '__main__':
    obj = Polit('https://polit.ru', 'https://polit.ru/news/')
    obj.parse_html()
    obj.write_info()
