from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import re
import requests
from user_agents import parse
from .models import Contact, PageView, ContactFormSettings, SiteStatistics
from django.views.decorators.csrf import csrf_exempt



def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_info(user_agent_string):
    """Parse user agent to get device information"""
    user_agent = parse(user_agent_string)
    
    # Determine device type
    if user_agent.is_mobile:
        device_type = 'mobile'
    elif user_agent.is_tablet:
        device_type = 'tablet'
    elif user_agent.is_pc:
        device_type = 'desktop'
    else:
        device_type = 'unknown'
    
    return {
        'device_type': device_type,
        'browser': f"{user_agent.browser.family} {user_agent.browser.version_string}",
        'operating_system': f"{user_agent.os.family} {user_agent.os.version_string}"
    }


def get_location_info(ip_address):
    """Get location information from IP address"""
    try:
        # Using a free IP geolocation service
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return {
                    'country': data.get('country', ''),
                    'city': data.get('city', ''),
                    'region': data.get('regionName', '')
                }
    except:
        pass
    
    return {'country': '', 'city': '', 'region': ''}


def track_page_view(request, page_url='/'):
    """Track page view and visitor analytics"""
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    referer = request.META.get('HTTP_REFERER', '')
    
    # Get device information
    device_info = get_device_info(user_agent)
    
    # Get location information
    location_info = get_location_info(ip_address)
    
    # Create page view record
    page_view = PageView.objects.create(
        ip_address=ip_address,
        user_agent=user_agent,
        referer=referer,
        page_url=page_url,
        country=location_info['country'],
        city=location_info['city'],
        region=location_info['region'],
        device_type=device_info['device_type'],
        browser=device_info['browser'],
        operating_system=device_info['operating_system'],
        session_id=request.session.session_key or ''
    )
    
    return page_view


def landing_page(request):
    """Main landing page view"""
    # Track page view
    track_page_view(request, '/')
    
    # Handle contact form submission
    if request.method == 'POST':
        return handle_contact_form(request)
    
    # Get some basic statistics for display
    total_views = PageView.objects.count()
    total_contacts = Contact.objects.count()
    
    context = {
        'total_views': total_views,
        'total_contacts': total_contacts,
    }
    
    return render(request, 'landing.html', context)

@csrf_exempt
def handle_contact_form(request):
    """Handle contact form submission"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'})
    
    try:
        # Get form data
        name = request.POST.get('name', '').strip()
        whatsapp = request.POST.get('whatsapp', '').strip()
        email = request.POST.get('email', '').strip()
        project_description = request.POST.get('project_description', '').strip()
        attachment = request.FILES.get('attachment')
        
        # Validate required fields
        if not all([name, whatsapp, email, project_description]):
            return JsonResponse({
                'success': False, 
                'error': 'Todos os campos obrigatórios devem ser preenchidos'
            })
        
        # Validate email format
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email):
            return JsonResponse({
                'success': False, 
                'error': 'Email inválido'
            })
        
        # Validate WhatsApp format
        whatsapp_clean = re.sub(r'\D', '', whatsapp)
        if len(whatsapp_clean) < 10 or len(whatsapp_clean) > 11:
            return JsonResponse({
                'success': False, 
                'error': 'Número de WhatsApp inválido'
            })
        
        # Get form settings
        form_settings = ContactFormSettings.get_settings()
        
        # Validate file upload if present
        if attachment:
            # Check file size
            max_size = form_settings.max_file_size_mb * 1024 * 1024  # Convert to bytes
            if attachment.size > max_size:
                return JsonResponse({
                    'success': False, 
                    'error': f'Arquivo muito grande. Máximo permitido: {form_settings.max_file_size_mb}MB'
                })
            
            # Check file type
            allowed_types = [ext.strip().lower() for ext in form_settings.allowed_file_types.split(',')]
            file_extension = attachment.name.split('.')[-1].lower()
            if file_extension not in allowed_types:
                return JsonResponse({
                    'success': False, 
                    'error': f'Tipo de arquivo não permitido. Tipos aceitos: {", ".join(allowed_types)}'
                })
        
        # Create contact record
        contact = Contact.objects.create(
            name=name,
            whatsapp=whatsapp,
            email=email,
            project_description=project_description,
            attachment=attachment
        )
        
        # Send notification email to admin
        if form_settings.email_notifications and form_settings.notification_email:
            try:
                subject = f'Novo contato do site - {name}'
                message = f'''
Novo contato recebido através do site:

Nome: {name}
Email: {email}
WhatsApp: {whatsapp}
Data: {contact.created_at.strftime("%d/%m/%Y às %H:%M")}

Descrição do Projeto:
{project_description}

{'Arquivo anexado: ' + contact.attachment_filename if contact.attachment else 'Nenhum arquivo anexado'}

Acesse o dashboard para mais detalhes: {request.build_absolute_uri('/dashboard/')}
                '''
                
                email_msg = EmailMessage(
                    subject=subject,
                    body=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[form_settings.notification_email]
                )
                
                # Attach file if present
                if contact.attachment:
                    email_msg.attach_file(contact.attachment.path)
                
                email_msg.send()
            except Exception as e:
                print(f"Erro ao enviar email de notificação: {e}")
        
        # Send auto-reply to user
        if form_settings.auto_reply_enabled:
            try:
                subject = form_settings.auto_reply_subject
                message = form_settings.auto_reply_message.format(
                    name=name,
                    email=email,
                    whatsapp=whatsapp,
                    date=contact.created_at.strftime("%d/%m/%Y às %H:%M")
                )
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Erro ao enviar resposta automática: {e}")
        
        # Return success response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': 'Mensagem enviada com sucesso! Entraremos em contato em breve.'
            })
        else:
            messages.success(request, 'Mensagem enviada com sucesso! Entraremos em contato em breve.')
            return redirect('landing_page')
    
    except Exception as e:
        print(f"Erro no formulário de contato: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'error': 'Erro interno do servidor. Tente novamente.'
            })
        else:
            messages.error(request, 'Erro ao enviar mensagem. Tente novamente.')
            return redirect('landing_page')


@require_http_methods(["GET"])
def portfolio_detail(request, project_id):
    """Portfolio project detail view (placeholder)"""
    # This would show detailed information about a portfolio project
    # For now, just track the page view
    track_page_view(request, f'/portfolio/{project_id}/')
    
    context = {
        'project_id': project_id,
    }
    
    return render(request, 'portfolio_detail.html', context)


@require_http_methods(["GET"])
def api_stats(request):
    """API endpoint for getting site statistics"""
    try:
        # Get basic statistics
        total_views = PageView.objects.count()
        unique_visitors = PageView.objects.values('ip_address').distinct().count()
        total_contacts = Contact.objects.count()
        
        # Get today's statistics
        today = timezone.now().date()
        today_views = PageView.objects.filter(timestamp__date=today).count()
        today_visitors = PageView.objects.filter(timestamp__date=today).values('ip_address').distinct().count()
        today_contacts = Contact.objects.filter(created_at__date=today).count()
        
        # Get top countries
        top_countries = PageView.objects.exclude(country='').values('country').annotate(
            count=Count('country')
        ).order_by('-count')[:5]
        
        # Get device breakdown
        device_stats = PageView.objects.values('device_type').annotate(
            count=Count('device_type')
        ).order_by('-count')
        
        # Get recent activity (last 7 days)
        from datetime import timedelta
        week_ago = timezone.now().date() - timedelta(days=7)
        recent_stats = []
        
        for i in range(7):
            date = week_ago + timedelta(days=i)
            daily_views = PageView.objects.filter(timestamp__date=date).count()
            daily_visitors = PageView.objects.filter(timestamp__date=date).values('ip_address').distinct().count()
            daily_contacts = Contact.objects.filter(created_at__date=date).count()
            
            recent_stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'views': daily_views,
                'visitors': daily_visitors,
                'contacts': daily_contacts
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'total': {
                    'views': total_views,
                    'visitors': unique_visitors,
                    'contacts': total_contacts
                },
                'today': {
                    'views': today_views,
                    'visitors': today_visitors,
                    'contacts': today_contacts
                },
                'top_countries': list(top_countries),
                'device_stats': list(device_stats),
                'recent_activity': recent_stats
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def robots_txt(request):
    """Robots.txt file for SEO"""
    from django.http import HttpResponse
    
    content = """User-agent: *
Allow: /

Sitemap: {}/sitemap.xml
""".format(request.build_absolute_uri('/'))
    
    return HttpResponse(content, content_type='text/plain')


def sitemap_xml(request):
    """Basic sitemap.xml for SEO"""
    from django.http import HttpResponse
    
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{}</loc>
        <lastmod>{}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>
""".format(
        request.build_absolute_uri('/'),
        timezone.now().strftime('%Y-%m-%d')
    )
    
    return HttpResponse(content, content_type='application/xml')


# Error handlers
def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)


def handler500(request):
    """Custom 500 error handler"""
    return render(request, '500.html', status=500)
