from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    # Main landing page
    path('', views.landing_page, name='landing_page'),
    
    # Portfolio detail (placeholder for future expansion)
    path('portfolio/<int:project_id>/', views.portfolio_detail, name='portfolio_detail'),
    
    # API endpoints
    path('api/stats/', views.api_stats, name='api_stats'),
    
    # SEO files
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
]

