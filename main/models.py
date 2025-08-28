from django.db import models
from django.utils import timezone
import os


def contact_file_upload_path(instance, filename):
    """Generate upload path for contact attachments"""
    return f'contact_attachments/{timezone.now().year}/{timezone.now().month}/{filename}'


class Contact(models.Model):
    """Model for contact form submissions"""
    name = models.CharField('Nome', max_length=100)
    whatsapp = models.CharField('WhatsApp', max_length=20)
    email = models.EmailField('Email')
    project_description = models.TextField('Descrição do Projeto')
    attachment = models.FileField(
        'Anexo', 
        upload_to=contact_file_upload_path, 
        blank=True, 
        null=True,
        help_text='Arquivo opcional (PDF, DOC, DOCX, TXT - máx. 10MB)'
    )
    created_at = models.DateTimeField('Data de Criação', auto_now_add=True)
    is_read = models.BooleanField('Lida', default=False)
    notes = models.TextField('Observações', blank=True, help_text='Notas internas sobre o contato')
    
    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} - {self.email}'
    
    @property
    def attachment_filename(self):
        """Get the filename of the attachment"""
        if self.attachment:
            return os.path.basename(self.attachment.name)
        return None
    
    @property
    def attachment_size(self):
        """Get the size of the attachment in MB"""
        if self.attachment:
            try:
                return round(self.attachment.size / (1024 * 1024), 2)
            except:
                return 0
        return 0


class PageView(models.Model):
    """Model for tracking page views and visitor analytics"""
    ip_address = models.GenericIPAddressField('Endereço IP')
    user_agent = models.TextField('User Agent', blank=True)
    referer = models.URLField('Referrer', blank=True, null=True)
    page_url = models.URLField('URL da Página', default='/')
    
    # Geographic information
    country = models.CharField('País', max_length=100, blank=True)
    city = models.CharField('Cidade', max_length=100, blank=True)
    region = models.CharField('Região/Estado', max_length=100, blank=True)
    
    # Device information
    device_type = models.CharField(
        'Tipo de Dispositivo', 
        max_length=20, 
        choices=[
            ('desktop', 'Desktop'),
            ('mobile', 'Mobile'),
            ('tablet', 'Tablet'),
            ('unknown', 'Desconhecido')
        ],
        default='unknown'
    )
    
    browser = models.CharField('Navegador', max_length=50, blank=True)
    operating_system = models.CharField('Sistema Operacional', max_length=50, blank=True)
    
    # Timestamps
    timestamp = models.DateTimeField('Data/Hora', auto_now_add=True)
    session_id = models.CharField('ID da Sessão', max_length=100, blank=True)
    
    # Engagement metrics
    time_on_page = models.PositiveIntegerField('Tempo na Página (segundos)', default=0)
    
    class Meta:
        verbose_name = 'Visualização de Página'
        verbose_name_plural = 'Visualizações de Página'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['country']),
        ]
    
    def __str__(self):
        return f'{self.ip_address} - {self.timestamp.strftime("%d/%m/%Y %H:%M")}'
    
    @property
    def is_unique_visitor(self):
        """Check if this is a unique visitor (first visit from this IP)"""
        return not PageView.objects.filter(
            ip_address=self.ip_address,
            timestamp__lt=self.timestamp
        ).exists()


class ContactFormSettings(models.Model):
    """Model for contact form settings and configuration"""
    email_notifications = models.BooleanField('Notificações por Email', default=True)
    notification_email = models.EmailField('Email para Notificações', default='admin@example.com')
    auto_reply_enabled = models.BooleanField('Resposta Automática', default=True)
    auto_reply_subject = models.CharField(
        'Assunto da Resposta Automática', 
        max_length=200, 
        default='Obrigado pelo seu contato!'
    )
    auto_reply_message = models.TextField(
        'Mensagem da Resposta Automática',
        default='''Olá {name},

Obrigado por entrar em contato conosco!

Recebemos sua mensagem e retornaremos em breve. Nosso tempo de resposta é de até 2 horas durante o horário comercial.

Detalhes da sua mensagem:
- Nome: {name}
- Email: {email}
- WhatsApp: {whatsapp}
- Data: {date}

Atenciosamente,
Equipe DevPro'''
    )
    
    # File upload settings
    max_file_size_mb = models.PositiveIntegerField('Tamanho Máximo do Arquivo (MB)', default=10)
    allowed_file_types = models.CharField(
        'Tipos de Arquivo Permitidos',
        max_length=200,
        default='pdf,doc,docx,txt',
        help_text='Separados por vírgula (ex: pdf,doc,docx,txt)'
    )
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Configuração do Formulário'
        verbose_name_plural = 'Configurações do Formulário'
    
    def __str__(self):
        return 'Configurações do Formulário de Contato'
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and ContactFormSettings.objects.exists():
            raise ValueError('Apenas uma configuração pode existir')
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class SiteStatistics(models.Model):
    """Model for storing site statistics and metrics"""
    date = models.DateField('Data', unique=True)
    total_views = models.PositiveIntegerField('Total de Visualizações', default=0)
    unique_visitors = models.PositiveIntegerField('Visitantes Únicos', default=0)
    contact_submissions = models.PositiveIntegerField('Envios de Contato', default=0)
    
    # Top countries (JSON field would be better, but keeping it simple)
    top_country_1 = models.CharField('País #1', max_length=100, blank=True)
    top_country_1_count = models.PositiveIntegerField('Contagem País #1', default=0)
    top_country_2 = models.CharField('País #2', max_length=100, blank=True)
    top_country_2_count = models.PositiveIntegerField('Contagem País #2', default=0)
    top_country_3 = models.CharField('País #3', max_length=100, blank=True)
    top_country_3_count = models.PositiveIntegerField('Contagem País #3', default=0)
    
    # Device breakdown
    desktop_views = models.PositiveIntegerField('Visualizações Desktop', default=0)
    mobile_views = models.PositiveIntegerField('Visualizações Mobile', default=0)
    tablet_views = models.PositiveIntegerField('Visualizações Tablet', default=0)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Estatística do Site'
        verbose_name_plural = 'Estatísticas do Site'
        ordering = ['-date']
    
    def __str__(self):
        return f'Estatísticas - {self.date.strftime("%d/%m/%Y")}'
    
    @classmethod
    def update_daily_stats(cls, date=None):
        """Update daily statistics for a given date"""
        if date is None:
            date = timezone.now().date()
        
        # Get or create stats for the date
        stats, created = cls.objects.get_or_create(date=date)
        
        # Calculate statistics
        daily_views = PageView.objects.filter(timestamp__date=date)
        stats.total_views = daily_views.count()
        stats.unique_visitors = daily_views.values('ip_address').distinct().count()
        
        # Contact submissions
        stats.contact_submissions = Contact.objects.filter(created_at__date=date).count()
        
        # Device breakdown
        stats.desktop_views = daily_views.filter(device_type='desktop').count()
        stats.mobile_views = daily_views.filter(device_type='mobile').count()
        stats.tablet_views = daily_views.filter(device_type='tablet').count()
        
        # Top countries
        country_stats = daily_views.exclude(country='').values('country').annotate(
            count=models.Count('country')
        ).order_by('-count')[:3]
        
        for i, country_stat in enumerate(country_stats, 1):
            setattr(stats, f'top_country_{i}', country_stat['country'])
            setattr(stats, f'top_country_{i}_count', country_stat['count'])
        
        stats.save()
        return stats
