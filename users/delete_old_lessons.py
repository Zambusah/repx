from django.core.management.base import BaseCommand
from reps.models import Lesson  # sostituisci 'your_app' con il nome della tua app
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Elimina tutte le lezioni con data passata'

    def handle(self, *args, **kwargs):
        today = now().date()
        deleted_count, _ = Lesson.objects.filter(date__lt=today).delete()
        self.stdout.write(self.style.SUCCESS(f'{deleted_count} lezioni passate eliminate.'))
