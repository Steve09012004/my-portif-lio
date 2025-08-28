from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.conf import settings
import csv
import io
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from main.models import Contact, PageView, ContactFormSettings, SiteStatistics


def dashboard_login(request):
    """Dashboard login view"""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard_home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:dashboard_home')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    
    return render(request, 'dashboard/login.html')


def dashboard_logout(request):
    """Dashboard logout view"""
    logout(request)
    messages.success(request, 'Logout realizado com sucesso.')
    return redirect('dashboard:dashboard_login')


@login_required
def dashboard_home(request):
    """Dashboard home page with statistics"""
    # Get basic statistics
    total_contacts = Contact.objects.count()
    unread_contacts = Contact.objects.filter(is_read=False).count()
    total_views = PageView.objects.count()
    unique_visitors = PageView.objects.values('ip_address').distinct().count()
    
    # Get today's statistics
    today = timezone.now().date()
    today_contacts = Contact.objects.filter(created_at__date=today).count()
    today_views = PageView.objects.filter(timestamp__date=today).count()
    today_visitors = PageView.objects.filter(timestamp__date=today).values('ip_address').distinct().count()
    
    # Get recent contacts (last 5)
    recent_contacts = Contact.objects.order_by('-created_at')[:5]
    
    # Get top countries (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    top_countries = PageView.objects.filter(
        timestamp__date__gte=thirty_days_ago
    ).exclude(country='').values('country').annotate(
        count=Count('country')
    ).order_by('-count')[:5]
    
    # Get device breakdown (last 30 days)
    device_stats = PageView.objects.filter(
        timestamp__date__gte=thirty_days_ago
    ).values('device_type').annotate(
        count=Count('device_type')
    ).order_by('-count')
    
    # Get daily statistics for the last 7 days
    daily_stats = []
    for i in range(7):
        date = today - timedelta(days=i)
        daily_contacts = Contact.objects.filter(created_at__date=date).count()
        daily_views = PageView.objects.filter(timestamp__date=date).count()
        daily_visitors = PageView.objects.filter(timestamp__date=date).values('ip_address').distinct().count()
        
        daily_stats.append({
            'date': date.strftime('%d/%m'),
            'contacts': daily_contacts,
            'views': daily_views,
            'visitors': daily_visitors
        })
    
    daily_stats.reverse()  # Show oldest to newest
    
    context = {
        'total_contacts': total_contacts,
        'unread_contacts': unread_contacts,
        'total_views': total_views,
        'unique_visitors': unique_visitors,
        'today_contacts': today_contacts,
        'today_views': today_views,
        'today_visitors': today_visitors,
        'recent_contacts': recent_contacts,
        'top_countries': top_countries,
        'device_stats': device_stats,
        'daily_stats': daily_stats,
    }
    
    return render(request, 'dashboard/home.html', context)


@login_required
def contacts_list(request):
    """List all contacts with filtering and search"""
    contacts = Contact.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        contacts = contacts.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(whatsapp__icontains=search_query) |
            Q(project_description__icontains=search_query)
        )
    
    # Filter by read status
    status_filter = request.GET.get('status', '')
    if status_filter == 'unread':
        contacts = contacts.filter(is_read=False)
    elif status_filter == 'read':
        contacts = contacts.filter(is_read=True)
    
    # Filter by date range
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            contacts = contacts.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            contacts = contacts.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Order by creation date (newest first)
    contacts = contacts.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(contacts, 20)  # Show 20 contacts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'total_contacts': contacts.count(),
    }
    
    return render(request, 'dashboard/contacts_list.html', context)


@login_required
def contact_detail(request, contact_id):
    """View contact details and mark as read"""
    contact = get_object_or_404(Contact, id=contact_id)
    
    # Mark as read when viewed
    if not contact.is_read:
        contact.is_read = True
        contact.save()
    
    # Handle notes update
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        contact.notes = notes
        contact.save()
        messages.success(request, 'Observações atualizadas com sucesso.')
        return redirect('dashboard:contact_detail', contact_id=contact.id)
    
    context = {
        'contact': contact,
    }
    
    return render(request, 'dashboard/contact_detail.html', context)


@login_required
def export_contacts_csv(request):
    """Export contacts to CSV"""
    # Get filtered contacts (same logic as contacts_list)
    contacts = Contact.objects.all()
    
    # Apply same filters as in contacts_list
    search_query = request.GET.get('search', '')
    if search_query:
        contacts = contacts.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(whatsapp__icontains=search_query) |
            Q(project_description__icontains=search_query)
        )
    
    status_filter = request.GET.get('status', '')
    if status_filter == 'unread':
        contacts = contacts.filter(is_read=False)
    elif status_filter == 'read':
        contacts = contacts.filter(is_read=True)
    
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            contacts = contacts.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            contacts = contacts.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass
    
    contacts = contacts.order_by('-created_at')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="contatos_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Nome', 'Email', 'WhatsApp', 'Descrição do Projeto', 'Data de Contato', 'Status', 'Anexo', 'Observações'])
    
    for contact in contacts:
        writer.writerow([
            contact.name,
            contact.email,
            contact.whatsapp,
            contact.project_description,
            contact.created_at.strftime('%d/%m/%Y %H:%M'),
            'Lida' if contact.is_read else 'Não lida',
            contact.attachment_filename if contact.attachment else 'Nenhum',
            contact.notes
        ])
    
    return response


@login_required
def export_contacts_pdf(request):
    """Export contacts to PDF"""
    # Get filtered contacts (same logic as contacts_list)
    contacts = Contact.objects.all()
    
    # Apply same filters as in contacts_list (same code as CSV export)
    search_query = request.GET.get('search', '')
    if search_query:
        contacts = contacts.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(whatsapp__icontains=search_query) |
            Q(project_description__icontains=search_query)
        )
    
    status_filter = request.GET.get('status', '')
    if status_filter == 'unread':
        contacts = contacts.filter(is_read=False)
    elif status_filter == 'read':
        contacts = contacts.filter(is_read=True)
    
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            contacts = contacts.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            contacts = contacts.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass
    
    contacts = contacts.order_by('-created_at')
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contatos_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    # Create PDF document
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Add title
    title = Paragraph("Relatório de Contatos", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Add generation info
    info = Paragraph(f"Gerado em: {timezone.now().strftime('%d/%m/%Y às %H:%M')}", normal_style)
    elements.append(info)
    elements.append(Paragraph(f"Total de contatos: {contacts.count()}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Add contacts
    for contact in contacts:
        # Contact header
        contact_title = Paragraph(f"<b>{contact.name}</b>", heading_style)
        elements.append(contact_title)
        
        # Contact details
        details = [
            f"<b>Email:</b> {contact.email}",
            f"<b>WhatsApp:</b> {contact.whatsapp}",
            f"<b>Data:</b> {contact.created_at.strftime('%d/%m/%Y às %H:%M')}",
            f"<b>Status:</b> {'Lida' if contact.is_read else 'Não lida'}",
        ]
        
        if contact.attachment:
            details.append(f"<b>Anexo:</b> {contact.attachment_filename}")
        
        for detail in details:
            elements.append(Paragraph(detail, normal_style))
        
        # Project description
        elements.append(Paragraph("<b>Descrição do Projeto:</b>", normal_style))
        elements.append(Paragraph(contact.project_description, normal_style))
        
        # Notes if any
        if contact.notes:
            elements.append(Paragraph("<b>Observações:</b>", normal_style))
            elements.append(Paragraph(contact.notes, normal_style))
        
        elements.append(Spacer(1, 20))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response


@login_required
def analytics(request):
    """Analytics page with detailed statistics"""
    # Get date range from request (default to last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    date_from = request.GET.get('date_from', start_date.strftime('%Y-%m-%d'))
    date_to = request.GET.get('date_to', end_date.strftime('%Y-%m-%d'))
    
    try:
        start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
    except ValueError:
        start_date = end_date - timedelta(days=30)
    
    # Get page views in date range
    page_views = PageView.objects.filter(
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date
    )
    
    # Get contacts in date range
    contacts = Contact.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )
    
    # Basic statistics
    total_views = page_views.count()
    unique_visitors = page_views.values('ip_address').distinct().count()
    total_contacts = contacts.count()
    
    # Top countries
    top_countries = page_views.exclude(country='').values('country').annotate(
        count=Count('country')
    ).order_by('-count')[:10]
    
    # Device breakdown
    device_stats = page_views.values('device_type').annotate(
        count=Count('device_type')
    ).order_by('-count')
    
    # Browser breakdown
    browser_stats = page_views.exclude(browser='').values('browser').annotate(
        count=Count('browser')
    ).order_by('-count')[:10]
    
    # Daily statistics
    daily_stats = []
    current_date = start_date
    while current_date <= end_date:
        daily_views = page_views.filter(timestamp__date=current_date).count()
        daily_visitors = page_views.filter(timestamp__date=current_date).values('ip_address').distinct().count()
        daily_contacts = contacts.filter(created_at__date=current_date).count()
        
        daily_stats.append({
            'date': current_date.strftime('%d/%m'),
            'views': daily_views,
            'visitors': daily_visitors,
            'contacts': daily_contacts
        })
        
        current_date += timedelta(days=1)
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'total_views': total_views,
        'unique_visitors': unique_visitors,
        'total_contacts': total_contacts,
        'top_countries': top_countries,
        'device_stats': device_stats,
        'browser_stats': browser_stats,
        'daily_stats': daily_stats,
    }
    
    return render(request, 'dashboard/analytics.html', context)


@login_required
def settings_view(request):
    """Dashboard settings page"""
    settings_obj = ContactFormSettings.get_settings()
    
    if request.method == 'POST':
        # Update settings
        settings_obj.email_notifications = request.POST.get('email_notifications') == 'on'
        settings_obj.notification_email = request.POST.get('notification_email', '')
        settings_obj.auto_reply_enabled = request.POST.get('auto_reply_enabled') == 'on'
        settings_obj.auto_reply_subject = request.POST.get('auto_reply_subject', '')
        settings_obj.auto_reply_message = request.POST.get('auto_reply_message', '')
        settings_obj.max_file_size_mb = int(request.POST.get('max_file_size_mb', 10))
        settings_obj.allowed_file_types = request.POST.get('allowed_file_types', '')
        
        settings_obj.save()
        messages.success(request, 'Configurações atualizadas com sucesso.')
        return redirect('dashboard:settings')
    
    context = {
        'settings': settings_obj,
    }
    
    return render(request, 'dashboard/settings.html', context)
