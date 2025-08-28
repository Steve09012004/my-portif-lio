from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Authentication
    path('login/', views.dashboard_login, name='dashboard_login'),
    path('logout/', views.dashboard_logout, name='dashboard_logout'),
    
    # Dashboard pages
    path('', views.dashboard_home, name='dashboard_home'),
    path('contacts/', views.contacts_list, name='contacts_list'),
    path('contacts/<int:contact_id>/', views.contact_detail, name='contact_detail'),
    path('analytics/', views.analytics, name='analytics'),
    path('settings/', views.settings_view, name='settings'),
    
    # Export functionality
    path('export/contacts/csv/', views.export_contacts_csv, name='export_contacts_csv'),
    path('export/contacts/pdf/', views.export_contacts_pdf, name='export_contacts_pdf'),
]

