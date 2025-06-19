from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerUser
from .models import Availability
from .models import TeacherSubject, Lesson
from django.db.models import Q
from datetime import time
from datetime import date, time, timedelta


def generate_time_choices(step_minutes=5):
    choices = []
    t = time(0, 0)
    # crea tutti gli orari da 00:00 a 23:30 ogni step
    while True:
        choices.append((t.strftime('%H:%M'), t.strftime('%H:%M')))
        # incrementa di step_minutes
        full_minutes = t.hour * 60 + t.minute + step_minutes
        if full_minutes >= 24 * 60:
            break
        t = time(full_minutes // 60, full_minutes % 60)
    return choices

TIME_CHOICES = generate_time_choices(15)

class CustomerUserCreationForm(UserCreationForm):
    is_student = forms.BooleanField(required=False, label="Studente")
    is_teacher = forms.BooleanField(required= False, label="Insegnante")

    class Meta:
        model=CustomerUser
        fields = ['Nome','Cognome', 'username', 'email', 'password1', 'password2', 'is_student', 'is_teacher']

class TeacherSubjectForm(forms.ModelForm):
    class Meta:
        model = TeacherSubject
        fields = ['subject']

    def clean(self):
        cleaned_data=super().clean()
        teacher_inside=self.initial.get('teacher')
        subject_inside=cleaned_data.get('subject')
    

        if teacher_inside and subject_inside:
            if TeacherSubject.objects.filter(
                teacher=teacher_inside,
                subject=subject_inside
            ).exists():
                raise forms.ValidationError("Hai già inserito questa materia")

    
        return cleaned_data




class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['day_of_week', 'start_time', 'end_time']
        labels = {
            'day_of_week': 'Giorno della settimana',
            'start_time':   'Ora di inizio',
            'end_time':     'Ora di fine',
        }
        help_texts = {
            'day_of_week': 'Seleziona il giorno della settimana',
          
        }
        widgets = {
            'day_of_week': forms.Select(),               # mantiene il select delle giornate
            'start_time':   forms.Select(choices=TIME_CHOICES),
            'end_time':     forms.Select(choices=TIME_CHOICES),
        }

    def clean(self):
        cleaned_data=super().clean()
        teacher=self.initial.get('teacher')
        day_of_week=cleaned_data.get('day_of_week')
        start_time=cleaned_data.get('start_time')
        end_time=cleaned_data.get('end_time')

        if teacher and day_of_week and start_time and end_time:
            if Availability.objects.filter(
                teacher=teacher,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            ).exists():
                raise forms.ValidationError("Hai già inserito questa disponibilità")

        if start_time and end_time:
            if start_time>=end_time:
                raise forms.ValidationError("L'orario di inizio deve essere prima di quello della fine della lezione")
            
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        overlapping = Availability.objects.filter(
            teacher=instance.teacher,
            day_of_week=instance.day_of_week
        ).filter(
            Q(start_time__lte=instance.end_time) &  # inizio ≤ fine nuovo
            Q(end_time__gte=instance.start_time)    # fine ≥ inizio nuovo
        )



        if overlapping.exists():
            new_start = min([instance.start_time] + [a.start_time for a in overlapping])
            new_end = max([instance.end_time] + [a.end_time for a in overlapping])
            overlapping.delete()
            instance.start_time = new_start
            instance.end_time = new_end

        if commit:
            instance.save()
        return instance
    


SUBJECT_CHOICES =  [
        ('math', 'Matematica'),
        ('physics', 'Fisica'),
        ('latin', 'Latino'),
        ('history','Storia'),
        ('science', 'Scienze'),
        ('english', 'Inglese'),
        ('french', 'Francese'),
    ]

DURATION_CHOICES = [
    (1, "1 ora"),
    (1.5, "1 ora e mezza"),
    (2, "2 ore"),
    (2.5, "2 ore e mezza"),
    (3, "3 ore"),
    (3.5, "3 ore e mezza"),
    (4, "4 ore"),
    (4.5,"4 ore e mezza"),
]

class LessonBookingForm(forms.ModelForm):
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES)
    start_time = forms.TimeField(
        label="Ora di inizio",
        widget=forms.Select(choices=[
            (time(hour, minute), f"{hour:02d}:{minute:02d}")
            for hour in range(8, 23)
            for minute in (0, 15, 30, 45)
        ])
    )
    duration = forms.ChoiceField(choices=DURATION_CHOICES, label="Durata")
    def clean_date(self):
        selected_date = self.cleaned_data['date']
        if selected_date < date.today():
            raise forms.ValidationError("Non puoi prenotare una lezione in una data passata.")
        return selected_date
    class Meta:
        model = Lesson
        fields = ['subject', 'date', 'start_time', 'duration']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget = forms.DateInput(attrs={'type': 'date'})

