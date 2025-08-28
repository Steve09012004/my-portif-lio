// ===== LOADING SCREEN =====
window.addEventListener('load', function() {
    const loadingScreen = document.getElementById('loading-screen');
    setTimeout(() => {
        loadingScreen.style.opacity = '0';
        setTimeout(() => {
            loadingScreen.style.display = 'none';
        }, 500);
    }, 1000);
});

// ===== NAVIGATION =====
document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.getElementById('navbar');
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');

    // Mobile menu toggle
    navToggle.addEventListener('click', function() {
        navMenu.classList.toggle('active');
        navToggle.classList.toggle('active');
    });

    // Close mobile menu when clicking on a link
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navMenu.classList.remove('active');
            navToggle.classList.remove('active');
        });
    });

    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Smooth scrolling for navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const offsetTop = targetSection.offsetTop - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Active navigation link highlighting
    window.addEventListener('scroll', function() {
        let current = '';
        const sections = document.querySelectorAll('section');
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (scrollY >= (sectionTop - 200)) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    });
});

// ===== PORTFOLIO FILTER =====
document.addEventListener('DOMContentLoaded', function() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const portfolioItems = document.querySelectorAll('.portfolio-item');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            filterBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');

            const filterValue = this.getAttribute('data-filter');

            portfolioItems.forEach(item => {
                if (filterValue === 'all' || item.classList.contains(filterValue)) {
                    item.style.display = 'block';
                    setTimeout(() => {
                        item.style.opacity = '1';
                        item.style.transform = 'translateY(0)';
                    }, 100);
                } else {
                    item.style.opacity = '0';
                    item.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        item.style.display = 'none';
                    }, 300);
                }
            });
        });
    });
});

// ===== TESTIMONIALS SLIDER =====
document.addEventListener('DOMContentLoaded', function() {
    const testimonialItems = document.querySelectorAll('.testimonial-item');
    const prevBtn = document.querySelector('.testimonial-prev');
    const nextBtn = document.querySelector('.testimonial-next');
    const dots = document.querySelectorAll('.testimonial-dots .dot');
    let currentSlide = 0;

    function showSlide(index) {
        // Hide all slides
        testimonialItems.forEach(item => {
            item.classList.remove('active');
        });

        // Remove active class from all dots
        dots.forEach(dot => {
            dot.classList.remove('active');
        });

        // Show current slide
        testimonialItems[index].classList.add('active');
        dots[index].classList.add('active');
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % testimonialItems.length;
        showSlide(currentSlide);
    }

    function prevSlide() {
        currentSlide = (currentSlide - 1 + testimonialItems.length) % testimonialItems.length;
        showSlide(currentSlide);
    }

    // Event listeners
    if (nextBtn) nextBtn.addEventListener('click', nextSlide);
    if (prevBtn) prevBtn.addEventListener('click', prevSlide);

    // Dot navigation
    dots.forEach((dot, index) => {
        dot.addEventListener('click', function() {
            currentSlide = index;
            showSlide(currentSlide);
        });
    });

    // Auto-play slider
    setInterval(nextSlide, 5000);
});

// ===== CONTACT FORM =====
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.querySelector('.contact-form');
    const submitBtn = document.querySelector('.btn-submit');
    const fileInput = document.getElementById('attachment');
    const fileLabel = document.querySelector('.file-upload-label span');

    // File upload handling
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const fileName = this.files[0].name;
                fileLabel.textContent = `Arquivo selecionado: ${fileName}`;
            } else {
                fileLabel.textContent = 'Clique para selecionar ou arraste o arquivo aqui';
            }
        });
    }

    // Phone number formatting
    const whatsappInput = document.getElementById('whatsapp');
    if (whatsappInput) {
        whatsappInput.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            if (value.length >= 11) {
                value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
            } else if (value.length >= 7) {
                value = value.replace(/(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
            } else if (value.length >= 3) {
                value = value.replace(/(\d{2})(\d{0,5})/, '($1) $2');
            }
            this.value = value;
        });
    }

    // Form validation
    function validateForm() {
        let isValid = true;
        const requiredFields = ['name', 'whatsapp', 'email', 'project_description'];
        
        requiredFields.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            const errorElement = document.getElementById(fieldName + '-error');
            
            if (!field.value.trim()) {
                showError(field, errorElement, 'Este campo é obrigatório');
                isValid = false;
            } else {
                hideError(field, errorElement);
                
                // Email validation
                if (fieldName === 'email') {
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(field.value)) {
                        showError(field, errorElement, 'Digite um email válido');
                        isValid = false;
                    }
                }
                
                // WhatsApp validation
                if (fieldName === 'whatsapp') {
                    const phoneRegex = /^\(\d{2}\)\s\d{4,5}-\d{4}$/;
                    if (!phoneRegex.test(field.value)) {
                        showError(field, errorElement, 'Digite um número válido: (11) 99999-9999');
                        isValid = false;
                    }
                }
            }
        });
        
        return isValid;
    }

    function showError(field, errorElement, message) {
        field.style.borderColor = '#e74c3c';
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    }

    function hideError(field, errorElement) {
        field.style.borderColor = '#e1e5e9';
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }

    // Form submission
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!validateForm()) {
                return;
            }

            // Show loading state
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;

            // Create FormData object
            const formData = new FormData(this);

            // Submit form via AJAX
            fetch(window.location.pathname, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Mensagem enviada com sucesso! Entraremos em contato em breve.', 'success');
                    contactForm.reset();
                    fileLabel.textContent = 'Clique para selecionar ou arraste o arquivo aqui';
                } else {
                    showNotification('Erro ao enviar mensagem. Tente novamente.', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Erro ao enviar mensagem. Tente novamente.', 'error');
            })
            .finally(() => {
                // Hide loading state
                submitBtn.classList.remove('loading');
                submitBtn.disabled = false;
            });
        });
    }
});

// ===== NOTIFICATIONS =====
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;

    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? '#27ae60' : '#e74c3c'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        z-index: 10000;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        max-width: 400px;
    `;

    // Add to page
    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);

    // Close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => notification.remove(), 300);
    });

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

// ===== BACK TO TOP BUTTON =====
document.addEventListener('DOMContentLoaded', function() {
    const backToTopBtn = document.getElementById('back-to-top');

    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            backToTopBtn.classList.add('visible');
        } else {
            backToTopBtn.classList.remove('visible');
        }
    });

    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});

// ===== SCROLL ANIMATIONS =====
document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS (Animate On Scroll)
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 1000,
            once: true,
            offset: 100
        });
    }

    // Custom scroll animations for elements without AOS
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    
    function checkScroll() {
        animateElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;
            
            if (elementTop < window.innerHeight - elementVisible) {
                element.classList.add('animated');
            }
        });
    }

    window.addEventListener('scroll', checkScroll);
    checkScroll(); // Check on load
});

// ===== TYPING ANIMATION =====
document.addEventListener('DOMContentLoaded', function() {
    const codeLines = document.querySelectorAll('.code-line');
    
    codeLines.forEach((line, index) => {
        line.style.opacity = '0';
        line.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            line.style.transition = 'all 0.5s ease';
            line.style.opacity = '1';
            line.style.transform = 'translateX(0)';
        }, index * 200 + 1000);
    });
});

// ===== COUNTER ANIMATION =====
document.addEventListener('DOMContentLoaded', function() {
    const counters = document.querySelectorAll('.stat-number');
    let animated = false;

    function animateCounters() {
        if (animated) return;
        
        const heroSection = document.getElementById('home');
        const heroTop = heroSection.getBoundingClientRect().top;
        
        if (heroTop < window.innerHeight / 2) {
            animated = true;
            
            counters.forEach(counter => {
                const target = parseInt(counter.textContent.replace(/\D/g, ''));
                const suffix = counter.textContent.replace(/\d/g, '');
                let current = 0;
                const increment = target / 50;
                
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        counter.textContent = target + suffix;
                        clearInterval(timer);
                    } else {
                        counter.textContent = Math.floor(current) + suffix;
                    }
                }, 50);
            });
        }
    }

    window.addEventListener('scroll', animateCounters);
    animateCounters(); // Check on load
});

// ===== PARALLAX EFFECT =====
document.addEventListener('DOMContentLoaded', function() {
    const heroParticles = document.querySelector('.hero-particles');
    
    if (heroParticles) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            heroParticles.style.transform = `translateY(${rate}px)`;
        });
    }
});

// ===== PERFORMANCE OPTIMIZATIONS =====
// Debounce function for scroll events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Apply debounce to scroll events
const debouncedScroll = debounce(function() {
    // Scroll event handlers here
}, 10);

window.addEventListener('scroll', debouncedScroll);

// ===== ACCESSIBILITY IMPROVEMENTS =====
document.addEventListener('DOMContentLoaded', function() {
    // Add keyboard navigation support
    const focusableElements = document.querySelectorAll(
        'a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])'
    );

    // Add focus indicators
    focusableElements.forEach(element => {
        element.addEventListener('focus', function() {
            this.style.outline = '2px solid #667eea';
            this.style.outlineOffset = '2px';
        });

        element.addEventListener('blur', function() {
            this.style.outline = 'none';
        });
    });

    // Skip to main content link
    const skipLink = document.createElement('a');
    skipLink.href = '#home';
    skipLink.textContent = 'Pular para o conteúdo principal';
    skipLink.className = 'skip-link';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 6px;
        background: #667eea;
        color: white;
        padding: 8px;
        text-decoration: none;
        border-radius: 4px;
        z-index: 10000;
        transition: top 0.3s;
    `;

    skipLink.addEventListener('focus', function() {
        this.style.top = '6px';
    });

    skipLink.addEventListener('blur', function() {
        this.style.top = '-40px';
    });

    document.body.insertBefore(skipLink, document.body.firstChild);
});

// ===== ERROR HANDLING =====
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    // You can add error reporting here
});

// ===== CONSOLE EASTER EGG =====
console.log(`
%c🚀 DevPro Landing Page
%cDesenvolvido com ❤️ usando Django, HTML5, CSS3 e JavaScript
%cInteressado no código? Entre em contato!
`, 
'color: #667eea; font-size: 20px; font-weight: bold;',
'color: #333; font-size: 14px;',
'color: #666; font-size: 12px;'
);

