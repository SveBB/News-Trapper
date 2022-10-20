"""Скрапер для gazeta.ru"""
from scraper_abstract import Scraper

class Ria (Scraper):
    """Класс скрапера для ria.ru"""
    def parse_html(self):
        """Переопределенный метод парсинга"""
        items = self.html.select('.w_col_wide > a')

        for item in items:
            title = {'name': '', 'text': '', 'source': '', 'url': ''}
            title['name'] = self.name
            text = item.text
            title['text'] = text.replace("\n", "")
            title['source'] = self.target
            title['url'] = item.get('href')
            self.titles.append(title)

        return self.titles

if __name__ == '__main__':
    obj = Ria('газета.ru', 'https://www.gazeta.ru/', 'https://www.gazeta.ru/')
    obj.parse_html()
    obj.write_info()
