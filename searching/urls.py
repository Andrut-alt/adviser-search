from django.urls import path
from . import views

app_name = 'searching'

urlpatterns = [
    path('filter-teachers/', views.filter_teachers_view, name='filter_teachers'),
    path('teacher/<int:teacher_id>/', views.teacher_detail_view, name='teacher_detail'),
    path('slot/<int:slot_id>/request/', views.send_slot_request_view, name='send_request'),
    path('teacher/requests/', views.teacher_requests_view, name='teacher_requests'),
    path('request/<int:request_id>/approve/', views.approve_request_view, name='approve_request'),
    path('request/<int:request_id>/reject/', views.reject_request_view, name='reject_request'),
    path('teacher/slots/', views.teacher_slots_view, name='teacher_slots'),
    path('teacher/slots/create/', views.create_slot_view, name='create_slot'),
    path('teacher/slots/<int:slot_id>/delete/', views.delete_slot_view, name='delete_slot'),
    path('teacher/slots/<int:slot_id>/', views.slot_detail_view, name='slot_detail'),
]

