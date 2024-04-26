# Используем официальный базовый образ Python, основанный на Debian
FROM python:3.9.6

# Устанавливаем рабочий каталог
WORKDIR /medical_helper

# Устанавливаем переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y wget build-essential tcl
RUN wget https://www.sqlite.org/2021/sqlite-autoconf-3350500.tar.gz \
    && tar xvfz sqlite-autoconf-3350500.tar.gz \
    && cd sqlite-autoconf-3350500 \
    && ./configure \
    && make \
    && make install

RUN apt-get update \
    && apt-get install -y gcc python3-dev libpq-dev netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip
RUN pip install --upgrade pip
COPY ./requirements.txt .
# Устанавливаем зависимости проекта
RUN pip install -r requirements.txt

# Копируем entrypoint.sh и подготавливаем его
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /medical_helper/entrypoint.sh
RUN chmod +x /medical_helper/entrypoint.sh

ENV HOME=/medical_helper
ENV APP_HOME=/medical_helper/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

# Копируем оставшиеся файлы проекта
COPY . .

# Устанавливаем точку входа
ENTRYPOINT ["/medical_helper/entrypoint.sh"]
