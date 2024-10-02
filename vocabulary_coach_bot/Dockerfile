# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем pip и обновляем его
RUN pip install --upgrade pip

# Копируем рабочую директорию в контейнер
WORKDIR /app
COPY . /app

# Устанавливаем зависимости из requirements.txt (предполагается, что он у вас есть)
RUN pip install -r requirements.txt

# Команда для запуска бота
CMD ["python3", "bot_tg.py"]
