# Landing Page para Desenvolvedor - Projeto Django

## 📋 Descrição

Este é um projeto Django completo para uma landing page singlepage profissional, desenvolvida para promover serviços de desenvolvimento (sites, sistemas e aplicativos). O projeto inclui um front-end moderno e responsivo, além de um dashboard administrativo completo.

## 🚀 Funcionalidades

### Landing Page
- **Design moderno e responsivo** - 100% compatível com dispositivos móveis
- **Seção de apresentação** - Introdução profissional com estatísticas
- **Portfólio interativo** - Showcase de projetos com filtros por categoria
- **Depoimentos de clientes** - Carrossel com avaliações
- **Formulário de contato** - Com validação e upload de arquivos
- **Botão WhatsApp flutuante** - Para contato rápido
- **SEO otimizado** - Meta tags e estrutura semântica
- **Animações suaves** - Efeitos de scroll e transições

### Dashboard Administrativo
- **Sistema de login seguro** - Autenticação protegida
- **Painel de controle** - Estatísticas e métricas em tempo real
- **Gestão de contatos** - Visualização e gerenciamento de mensagens
- **Analytics avançado** - Gráficos de visitantes e origem geográfica
- **Exportação de dados** - CSV e PDF dos contatos
- **Filtros e busca** - Localização rápida de informações

## 🛠️ Tecnologias Utilizadas

### Backend
- **Django 5.2.5** - Framework web Python
- **SQLite** - Banco de dados (desenvolvimento)
- **Python 3.11** - Linguagem de programação

### Frontend
- **HTML5** - Estrutura semântica
- **CSS3** - Estilização moderna com Flexbox/Grid
- **JavaScript** - Interatividade e animações
- **Font Awesome** - Ícones profissionais
- **AOS Library** - Animações on scroll

### Dependências Python
- `django` - Framework web
- `pillow` - Processamento de imagens
- `python-decouple` - Gerenciamento de configurações
- `user-agents` - Detecção de dispositivos

## 📦 Instalação e Configuração

### 1. Pré-requisitos
```bash
# Python 3.11 ou superior
python --version

# pip (gerenciador de pacotes Python)
pip --version
```

### 2. Instalação das Dependências
```bash
# Navegar para o diretório do projeto
cd landing_page_project

# Instalar dependências
pip install django pillow python-decouple user-agents
```

### 3. Configuração do Banco de Dados
```bash
# Executar migrações
python manage.py makemigrations
python manage.py migrate

# Criar superusuário (opcional - já existe admin/admin123)
python manage.py createsuperuser
```

### 4. Executar o Servidor
```bash
# Iniciar servidor de desenvolvimento
python manage.py runserver

# Acessar em: http://localhost:8000
```

## 🔐 Credenciais de Acesso

### Dashboard Administrativo
- **URL**: `/dashboard/login/`
- **Usuário**: `admin`
- **Senha**: `admin123`

## 📁 Estrutura do Projeto

```
landing_page_project/
├── main/                          # App principal
│   ├── models.py                  # Modelos de dados
│   ├── views.py                   # Views da landing page
│   ├── urls.py                    # URLs do app
│   └── migrations/                # Migrações do banco
├── dashboard/                     # App do dashboard
│   ├── views.py                   # Views administrativas
│   ├── urls.py                    # URLs do dashboard
│   └── migrations/                # Migrações do dashboard
├── templates/                     # Templates HTML
│   ├── base.html                  # Template base
│   ├── landing.html               # Landing page
│   └── dashboard/                 # Templates do dashboard
├── static/                        # Arquivos estáticos
│   ├── css/                       # Estilos CSS
│   ├── js/                        # Scripts JavaScript
│   └── images/                    # Imagens do projeto
├── media/                         # Uploads de usuários
├── manage.py                      # Script de gerenciamento Django
├── .env.example                   # Exemplo de variáveis de ambiente
└── README.md                      # Esta documentação
```

## 🎨 Personalização

### Cores e Estilo
As cores principais podem ser alteradas no arquivo `static/css/style.css`:
```css
:root {
    --primary-color: #6c5ce7;
    --secondary-color: #a29bfe;
    --accent-color: #fd79a8;
    --success-color: #00b894;
    --warning-color: #fdcb6e;
    --danger-color: #e17055;
}
```

### Conteúdo
- **Textos**: Editar diretamente no template `templates/landing.html`
- **Imagens**: Substituir arquivos na pasta `static/images/`
- **Informações de contato**: Atualizar no template e nas views

### SEO
Atualizar meta tags no arquivo `templates/base.html`:
```html
<meta name="description" content="Sua descrição aqui">
<meta name="keywords" content="suas, palavras-chave, aqui">
```

## 📊 Analytics e Métricas

O sistema coleta automaticamente:
- **Visualizações da página** - Contador de acessos
- **Origem geográfica** - País/cidade dos visitantes
- **Dispositivos utilizados** - Desktop/Mobile/Tablet
- **Contatos recebidos** - Formulários enviados

## 🔧 Configurações de Produção

### Variáveis de Ambiente
Criar arquivo `.env` baseado no `.env.example`:
```env
SECRET_KEY=sua_chave_secreta_aqui
DEBUG=False
ALLOWED_HOSTS=seudominio.com,www.seudominio.com
```

### Banco de Dados
Para produção, considere usar PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nome_do_banco',
        'USER': 'usuario',
        'PASSWORD': 'senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Arquivos Estáticos
```bash
# Coletar arquivos estáticos para produção
python manage.py collectstatic
```

## 📱 Responsividade

O projeto é totalmente responsivo e otimizado para:
- **Desktop** - Telas grandes (1200px+)
- **Tablet** - Telas médias (768px - 1199px)
- **Mobile** - Telas pequenas (até 767px)

## 🚀 Deploy

### Opções de Deploy
1. **Heroku** - Plataforma como serviço
2. **DigitalOcean** - VPS com Docker
3. **AWS** - Elastic Beanstalk ou EC2
4. **Vercel** - Para frontend estático

### Checklist de Deploy
- [ ] Configurar variáveis de ambiente
- [ ] Atualizar ALLOWED_HOSTS
- [ ] Configurar banco de dados de produção
- [ ] Configurar arquivos estáticos
- [ ] Configurar HTTPS
- [ ] Testar todas as funcionalidades

## 🐛 Solução de Problemas

### Problemas Comuns

**1. Erro de CSRF**
```python
# Adicionar ao settings.py
CSRF_TRUSTED_ORIGINS = ['https://seudominio.com']
```

**2. Arquivos estáticos não carregam**
```bash
python manage.py collectstatic --clear
```

**3. Erro de migração**
```bash
python manage.py makemigrations --empty main
python manage.py migrate --fake-initial
```

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar a documentação do Django
2. Consultar os logs de erro
3. Revisar as configurações do projeto

## 📄 Licença

Este projeto foi desenvolvido para uso comercial. Todos os direitos reservados.

---

**Desenvolvido com ❤️ usando Django e tecnologias modernas**

