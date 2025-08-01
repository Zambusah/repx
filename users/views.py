from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomerUserCreationForm, AvailabilityForm, TeacherSubjectForm,LessonBookingForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Availability
from .models import TeacherSubject
from .models import  Lesson
from .models import CustomerUser
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from datetime import timedelta, datetime, time, date
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
import stripe 
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy


class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

custom_password_reset_view = CustomPasswordResetView.as_view()


def home_view(request):
    return render(request, 'users/home.html')



def register_view(request):
    if request.method == 'POST':
        form = CustomerUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request , user)
            if request.user.is_teacher:
                return redirect('dashboard_teacher')
            elif request.user.is_student:
                return redirect('dashboard_student')
    else:
        form = CustomerUserCreationForm()
    return render( request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form=AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user=form.get_user()
            login(request, user)
            if request.user.is_teacher:
                return redirect('dashboard_teacher')
            elif request.user.is_student:
                return redirect('dashboard_student')
    else:
        form= AuthenticationForm()
    return render(request, 'users/login.html', {'form':form})

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.is_teacher:
        availabilities= Availability.objects.filter(teacher=request.user)
        subjects= TeacherSubject.objects.filter(teacher=request.user)
        user=request.user
        context={
            'user':user,
            'availabilities':availabilities,
            'subjects' : subjects,
        }   
        return render(request, 'users/dashboard.html', context)
    
    if request.user.is_student:
        availabilities= Availability.objects.filter(teacher=request.user)
        subjects= TeacherSubject.objects.filter(teacher=request.user)
        user=request.user
        context={
            'user':user,
            'availabilities':availabilities,
            'subjects' : subjects,
        }   
        return render(request, 'users/dashboard.html', context)

@login_required
def dashboard__teacher_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_teacher:
        return redirect('login')

    availabilities= Availability.objects.filter(teacher=request.user)
    subjects= TeacherSubject.objects.filter(teacher=request.user)
    user=request.user
    lessons = Lesson.objects.filter(teacher=user).order_by('date', 'start_time')
    context={
        'user':user,
        'availabilities':availabilities,
        'subjects' : subjects,
        'lessons': lessons
        }   
    
    return render(request, 'users/dashboard_teacher.html', context)
    

@login_required
def dashboard__student_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_student:
        return redirect('login')
    
    user = request.user
    lessons = Lesson.objects.filter(student=user).order_by('date', 'start_time')
    return render(request, 'users/dashboard_student.html', {'lessons': lessons})


    

    


@login_required
def manage_availability_view(request):
    if not request.user.is_teacher:
        return redirect('dashboard')
    
    if request.method =='POST':
        form=AvailabilityForm(request.POST, initial={'teacher': request.user})
        form.instance.teacher = request.user
        if form.is_valid():
            availability=form.save(commit=False)
            #availability.teacher=request.user
            availability.save()
            return redirect('manage_availability')
    else:
        form=AvailabilityForm()
    
    user_availabilities = Availability.objects.filter(teacher=request.user)
    return render(request, 'users/manage_availability.html', {'form':form, 'availabilities' : user_availabilities})

@login_required
def delete_availability(request, pk):
    availability = get_object_or_404(Availability, pk=pk, teacher=request.user)
    availability.delete()
    return redirect('manage_availability')

@login_required
def manage_subjects_view(request):
    if not request.user.is_teacher:
        return redirect('dashboard')
    
    if request.method=='POST':
        form=TeacherSubjectForm(request.POST, initial={'teacher': request.user})#, initial={'teacher': request.user})
        form.instance.teacher = request.user
        if form.is_valid():
            subjects=form.save(commit=False)
            subjects.save()
            return redirect('manage_subjects')
    else:
        form=TeacherSubjectForm()
    
    user_subjects= TeacherSubject.objects.filter(teacher=request.user)
    return render(request, 'users/manage_subjects.html', {'form':form, 'subjects' : user_subjects})

@login_required
def delete_subject(request, pk):
    subject = get_object_or_404(TeacherSubject, pk=pk, teacher=request.user)
    subject.delete()
    return redirect('manage_subjects')




@login_required
def book_lesson_view(request):
    if not request.user.is_student:
        return redirect('dashboard')

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if request.method == 'POST':
        form = LessonBookingForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            date = form.cleaned_data['date']
            start_time = form.cleaned_data['start_time']
            duration = float(form.cleaned_data['duration'])
            
            start_dt = datetime.combine(date, start_time)
            end_dt = start_dt + timedelta(hours=duration)
            end_time = end_dt.time()

            # Trova insegnanti con quella materia e disponibili in quell'orario
            available_teachers = CustomerUser.objects.filter(
                is_teacher=True,
                subjects__subject=subject,
                availability__day_of_week=days_of_week[date.weekday()],
                availability__start_time__lte=start_time,
                availability__end_time__gte=end_time
            ).exclude(
                teacher_lessons__date=date,
                teacher_lessons__start_time=start_time
            ).distinct()

            if available_teachers.exists():
                teacher_id = available_teachers.order_by('?').first().id
                request.session['lesson_data'] = {
                    'subject': subject,
                    'date': str(date),
                    'start_time': str(start_time),
                    'end_time': str(end_time),
                    'teacher_id': teacher_id,
                }
                return redirect('confirm_lesson')

            else:
                form.add_error(None, "Nessun insegnante disponibile.")

    else:
        form = LessonBookingForm()

    return render(request, 'students/book_lesson.html', {'form': form})
            #print("Trovati:", available_teachers)

SUBJECTS_DICT = {
    'math': 'Matematica',
    'physics': 'Fisica',
    'latin': 'Latino',
    'history': 'Storia',
    'science': 'Scienze',
    'english': 'Inglese',
    'french': 'Francese',
}
@login_required
def confirm_lesson_view(request):
    data = request.session.get('lesson_data')
    if not data:
        return redirect('book_lesson')

    teacher = CustomerUser.objects.get(id=data['teacher_id'])

    # Usa il formato corretto per orari con i secondi
    date_obj = datetime.strptime(data['date'], "%Y-%m-%d").date()
    start_time_obj = datetime.strptime(data['start_time'], "%H:%M:%S").time()
    end_time_obj = datetime.strptime(data['end_time'], "%H:%M:%S").time()
    subject_display = SUBJECTS_DICT.get(data['subject'], data['subject'])

    return render(request, 'students/confirm_lesson.html', {
        'subject': data['subject'],
        'subject_ita': subject_display,
        'date': date_obj,
        'start_time': start_time_obj,
        'end_time': end_time_obj,
        'teacher': teacher,
    })


def video_call_view(request, token):
    lesson=get_object_or_404(Lesson, link__icontains=token)
    return render(request, 'video_call/room.html', {'lesson': lesson})




@csrf_exempt
def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': 'Lezione di ripetizione',
                },
                'unit_amount': 0000,  # prezzo in centesimi (es. €30,00)
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url = request.build_absolute_uri(reverse('success')),
        cancel_url='http://localhost:8000/cancel/',
    )
    return redirect(session.url, code=303)




@login_required
def success_view(request):
    data = request.session.get('lesson_data')
    if not data:
        return redirect('dashboard_student')

    # Recupera i dati salvati in sessione
    subject = data['subject']
    date = data['date']
    start_time = data['start_time']
    end_time = data['end_time']
    teacher_id = data['teacher_id']

    # Recupera l'insegnante
    try:
        teacher = CustomerUser.objects.get(id=teacher_id)
    except CustomerUser.DoesNotExist:
        return redirect('dashboard_student')

    # Genera il link della videochiamata
    link = request.build_absolute_uri(
        reverse('video_call', args=[get_random_string(length=32)])
    )

    # Crea la lezione
    lesson = Lesson.objects.create(
        student=request.user,
        teacher=teacher,
        subject=subject,
        date=date,
        start_time=start_time,
        end_time=end_time,
        link=link
    )

    # Invia le mail a studente e insegnante
    send_mail(
        'Conferma Lezione',
        f'Hai prenotato una lezione su REPS. Link: {link}',
        settings.DEFAULT_FROM_EMAIL,
        [request.user.email],
    )
    send_mail(
        'Nuova lezione assegnata',
        f'Hai una nuova lezione con {request.user.username}. Link: {link}',
        settings.DEFAULT_FROM_EMAIL,
        [teacher.email],
    )

    # Rimuove i dati dalla sessione
    del request.session['lesson_data']

    return render(request, 'payments/success.html', {'lesson': lesson})


@login_required
def cancel_view(request):

    return render(request, 'payments/cancel.html')






