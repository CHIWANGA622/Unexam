from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('exams/', views.exam_list_view, name='exam_list'),
    path('exam/<int:exam_id>/', views.exam_view, name='exam'),
    path('confirm/<int:exam_id>/', views.confirm_submit_view, name='confirm_submit'),
    path('my-results/', views.my_results_view, name='my_results'),
    path('results/', views.results_view, name='results'),
    path('change-password/', views.change_password_view, name='change_password')
]