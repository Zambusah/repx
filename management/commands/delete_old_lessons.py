from django.core.management.base import BaseCommand
from users.models import Lesson  # sostituisci 'your_app' con il nome della tua app
from datetime import date

class Command(BaseCommand):
    help = 'Elimina tutte le lezioni passate'

    def handle(self, *args, **kwargs):
        today = date.today()
        deleted_count, _ = Lesson.objects.filter(date__lte=today).delete()
        self.stdout.write(self.style.SUCCESS(f'{deleted_count} lezioni passate eliminate.'))
