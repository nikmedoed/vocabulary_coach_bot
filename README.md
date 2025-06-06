# Telegram бот для заучивания ответов на вопросы

Этот бот должен помочь в заучивании ответов на вопросы.

Пока что в нём реализовано 2 варианта тренировок:
- Введи ответ в точности
- Выбери ответ из 8

Исходно он разрабатывался для заучивания слов и выражений, но вы можете использовать его как угодно.

На данный момент база данных пользователя размещается в гугл табличке, которую нужно развернуть в вашем аккаунте.
[Это просто, вот инструкция](docs/deploy_table.md)

БД в таблице - простой интерфейс.
От вас нужно вносить построчно ==ответ (слово) - вопрос - подсказка==, а бот подхватит эти данные при следующем вопросе. Накопленные задания не потеряются при поломке бота.

- Развёрнутый бот. Потребуется лишь сделать копию таблицы.
https://t.me/vocabulary_coach_bot

- Другие мои проекты и исследования тут: https://t.me/etonikmedoed

- [Инструкция по созданию копии таблицы и активации работы с ботом](docs/deploy_table.md)

## Планы
Если ботом будут активно пользоваться, то постепенно добавлю:

- Статистику по тренировке
- Статистику по пользователю, общий рейтинг
- Серверную базу данных
	- Загрузка и выгрузка в excel
	- Добавление слов по одному
	- База пояснений слов из какого-нибудь словаря (oxford), т.е. достаточно будет прислать слово
	- и другие фичи
- Диагностику ошибок
- Новые режимы игры
	- Чужие слова
	- Слова из словаря
	- Виселица
	- Введи перевод
	- "Произнеси слово"
- Поддержка разных тем вопросов
- Мультиязычность

## Requirements

- Redis-server
- python
	- asyncio
	- aiogram
