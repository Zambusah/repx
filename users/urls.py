from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

"""
path('users/', include('users.urls')),
path('bookings/', include('bookings.urls')),
path('schedules/', include('schedules.urls')),
"""

urlpatterns=[
path('', views.home_view, name='home'),
path('admin/', admin.site.urls),
path('register/', views.register_view, name='register'),
path('login/', views.login_view, name='login'),
path('logout/', views.logout_view, name='logout'),
path('dashboard/', views.dashboard_view, name='dashboard'),
path('disponibilita/', views.manage_availability_view, name='manage_availability'),
path('availability/delete/<int:pk>/', views.delete_availability, name='delete_availability'),
path('subjects/', views.manage_subjects_view, name='manage_subjects'),
path('subject/delete/<int:pk>/', views.delete_subject, name='delete_subject'),
path('book_lesson/', views.book_lesson_view,name='book_lesson' ),
path('dashboard_teacher/', views.dashboard__teacher_view, name='dashboard_teacher'),
path('dashboard_student/', views.dashboard__student_view, name='dashboard_student'),
path('call/str<str:token>/', views.video_call_view, name='video_call'),
path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
path('success/', views.success_view, name='success'),
path('cancel/', views.cancel_view, name='cancel'),
path('confirm_lesson/', views.confirm_lesson_view, name='confirm_lesson'),
]