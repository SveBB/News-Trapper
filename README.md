# Telegram Bot "News Trapper" ("ONLY HOT NEWS")
[@NewsTrapperBot](https://t.me/NewsTrapperBot) в [Telegram](https://telegram.org), бот позволяет просамтривать новостные топики из разныех источников и подписываться на них. Бот сделан с помощью [Aiogram Bot Api](https://docs.aiogram.dev/en/latest/).

License: MIT

*The code has NOT been polished and is provided "as is". There's a lot of code that is redundant and there are tons of improvements that can be made.*

# FAQ

Q: Откуда беруться новости?

A: Новости собирают скрипты-скрэперы из /scrapers

Q: Как подготовить программу к работе?

A: Достаточно лишь записать токен бота и период рассылки в config.py

Q: Сколько источников есть у бота?

A: На данный момент есть 3 рабочих скрэпера (с сайтом РИА новости возникают проблемы), но благодоря описаному шаблону легко добавить новые скрэперы

Q: Зачем мне это надо?

A: Возможно получится создать действительно удобный инструмент и больше не надо будет ждать почтальона с газетой

# Launch
'docker-compose up --build' - собрать и запустить докер контейнер

## Author
(C) 2020 by [Vadim Solopov](https://t.me/tohellim).
