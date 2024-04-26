from django.core.management.base import BaseCommand
from aiogram import executor
from bot.bot import dp


class Command(BaseCommand):
    help = 'Запускает телеграм бота'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Запуск бота'))
        executor.start_polling(dp, skip_updates=True)
