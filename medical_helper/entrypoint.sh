#!/bin/sh

# Проверка доступности базы данных Postgres
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    # Цикл ожидания доступности Postgres
    while ! nc -z "$DB_HOST" "$DB_PORT"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Очистка базы данных и применение миграций
python manage.py flush --no-input
python manage.py migrate

# Сбор статических файлов
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Создание суперпользователя
echo "Creating superuser..."
echo "from django.contrib.auth.models import User; User.objects.create_superuser('$SUPERUSER_LOGIN', '', '$SUPERUSER_PASSWORD')" | python manage.py shell

echo "Starting the bot in the background..."
python manage.py startbot &

exec "$@"
