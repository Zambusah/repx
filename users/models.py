from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string


class CustomerUser(AbstractUser):
    is_student=models.BooleanField(default=False)
    is_teacher=models.BooleanField(default=False)
    Nome=models.CharField(max_length=50, blank=True)
    Cognome=models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.username
    

SUBJECT_CHOICES =  [
        ('math', 'Matematica'),
        ('physics', 'Fisica'),
        ('latin', 'Latino'),
        ('history','Storia'),
        ('science', 'Scienze'),
        ('english', 'Inglese'),
        ('french', 'Francese'),
    ]

class TeacherSubject(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subjects")
    subject= models.CharField(max_length=50, choices=SUBJECT_CHOICES)


    def __str__(self):
        materie={
            'math': 'Matematica',
            'physics': 'Fisica',
            'latin' : 'Latino',
            'history' : 'Storia',
            'science' : 'Scienze',
            'english': 'Inglese', 
            'french' : 'Francese',
        }
        materia=materie.get(self.subject, self.subject)
        return materia

DAY_CHOICES=[
        ('Monday', 'Lunedì'),
        ('Tuesday', 'Martedì'),
        ('Wednesday', 'Mercoledì'),
        ('Thursday', 'Giovedì'),
        ('Friday', 'Venerdì'),
        ('Saturday', 'Sabato'),
        ('Sunday', 'Domenica'),
    ]

class Availability(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="availability")
    day_of_week= models.CharField(max_length=10, choices=DAY_CHOICES )

    start_time = models.TimeField()
    end_time=models.TimeField()

    def __str__(self):
        giorni_settimana= {
        'Monday': 'Lunedì',
        'Tuesday': 'Martedì',
        'Wednesday': 'Mercoledì',
        'Thursday': 'Giovedì',
        'Friday': 'Venerdì',
        'Saturday': 'Sabato',
        'Sunday': 'Domenica',
        }
        giorno=giorni_settimana.get(self.day_of_week, self.day_of_week)
        return f"{self.teacher.username} - {giorno}{self.start_time.strftime('%H:%M')} → {self.end_time.strftime('%H:%M')}"



class Lesson(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_lessons')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='teacher_lessons')
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    link=models.URLField(blank=True, null=True)

    def __str__(self):
        """
        giorni_settimana= {
        'Monday': 'Lunedì',
        'Tuesday': 'Martedì',
        'Wednesday': 'Mercoledì',
        'Thursday': 'Giovedì',
        'Friday': 'Venerdì',
        'Saturday': 'Sabato',
        'Sunday': 'Domenica',
        }
        giorno=giorni_settimana.get(self.day_of_week, self.day_of_week)"""
        return f"{self.subject} - {self.date} {self.start_time}"


# Create your models here.
