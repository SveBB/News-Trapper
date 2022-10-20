"""Скрапер для ria.ru"""
from scraper_abstract import Scraper

class Ria (Scraper):
    """Класс скрапера для ria.ru"""
    def parse_html(self):
        """Переопределенный метод парсинга"""
        items = self.html.select('.cell-list__list > .m-no-image > a')

        for item in items:
            title = {'name': '', 'text': '', 'source': '', 'url': ''}
            title['name'] = self.name
            title['text'] = item.text
            title['source'] = self.target
            title['url'] = item.get('href')
            self.titles.append(title)

        return self.titles

if __name__ == '__main__':
    obj = Ria('РИА НОВОСТИ', 'https://ria.ru/', 'https://ria.ru/')
    obj.parse_html()
    obj.write_info()
