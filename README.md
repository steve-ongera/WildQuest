# 🌍 WildQuest - Kenya Travel Agency Platform

**Developed by Steve Ongera**

WildQuest is a modern Django-powered travel agency web application specifically designed for Kenya's vibrant tourism and travel industry. This comprehensive platform enables seamless exploration, booking, and management of travel experiences across Kenya's diverse destinations—from the iconic wildlife safaris in Maasai Mara to the pristine beach holidays in Diani and adventurous mountain climbing expeditions.

[![Django](https://img.shields.io/badge/Django-4.x-092E20?style=flat-square&logo=django&logoColor=white)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org/)
[![M-Pesa](https://img.shields.io/badge/M--Pesa-00D13B?style=flat-square&logo=safaricom&logoColor=white)](https://developer.safaricom.co.ke/)

## 🎯 Project Vision

WildQuest bridges the gap between Kenya's rich tourism offerings and modern digital booking experiences. Built with deep understanding of the local market, this platform addresses the unique needs of Kenyan travelers and tour operators, incorporating familiar payment methods like M-Pesa and WhatsApp communication preferences.

## 🚀 Key Features

### 👑 **For Travel Agency Administrators**
- **📅 Comprehensive Event Management**: Create and manage diverse travel experiences including safaris, road trips, summits, cultural tours, and beach holidays
- **🎯 Dynamic Capacity Control**: Set participant limits with real-time availability tracking and automated waitlist management
- **💰 Flexible Pricing Models**: Configure multiple pricing tiers (Regular, VIP, Premium, Budget) with group discounts
- **📸 Rich Media Management**: Upload and organize event galleries with primary image selection and alt-text optimization
- **📊 Advanced Analytics Dashboard**: Monitor booking trends, revenue analytics, and customer demographics
- **💬 Communication Hub**: Manage WhatsApp booking requests, email inquiries, and customer support tickets
- **📋 Content Management**: Create detailed itineraries, FAQs, event features, and comprehensive event descriptions

### 🎫 **For Travel Enthusiasts (Customers)**
- **🔍 Intuitive Event Discovery**: Browse events by category, destination, price range, and availability
- **👥 Flexible Group Bookings**: Book for individuals, families, or groups without mandatory account registration
- **📱 Multiple Booking Channels**: 
  - Direct WhatsApp booking integration
  - Online booking with instant M-Pesa payments
  - Phone and email booking options
- **📋 Detailed Event Information**: Access comprehensive event details, photo galleries, itineraries, and real customer reviews
- **⭐ Community Reviews**: Read authentic reviews and share experiences with fellow travelers
- **🎫 Guest Checkout**: Complete bookings without creating user accounts for maximum convenience

### 🇰🇪 **Kenya-Specific Innovations**
- **📱 M-Pesa Integration**: Seamless mobile money payments through Safaricom's M-Pesa API
- **💬 WhatsApp Booking**: Native WhatsApp integration for natural customer communication
- **🗺️ Regional Coverage**: Comprehensive mapping of Kenya's counties and regions with GPS coordinates
- **🏛️ Cultural Sensitivity**: Support for local languages, customs, and cultural preferences
- **📞 Local Contact Formats**: Kenya-specific phone number and address validation

## 🏗️ Technical Architecture

### **Core Technology Stack**
- **Backend Framework**: Django 4.x with Python 3.9+
- **Database**: PostgreSQL (production) / SQLite (development)
- **Payment Gateway**: M-Pesa Daraja API integration
- **Image Processing**: Pillow for optimized image handling
- **Admin Interface**: Extensively customized Django Admin
- **API Framework**: Django REST Framework (optional)

### **Key Models & Architecture**
```python
# Core Models Structure
Event → EventImage, PricingTier, FAQ, Itinerary
Booking → BookingParticipant, Payment
WhatsAppBooking → Booking (conversion workflow)
Location → Event (regional mapping)
Review → Event (customer feedback)
```

## 📦 Quick Start Guide

### **Prerequisites**
- Python 3.9 or higher
- Django 4.x
- PostgreSQL 12+ (recommended for production)
- Virtual environment (venv or conda)
- Git for version control

### **Installation Process**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/steveongera/wildquest.git
   cd wildquest
   ```

2. **Set Up Virtual Environment**
   ```bash
   # Create virtual environment
   python -m venv wildquest_env
   
   # Activate environment
   # On Linux/MacOS:
   source wildquest_env/bin/activate
   # On Windows:
   wildquest_env\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create `.env` file in project root:
   ```env
   # Core Django Settings
   SECRET_KEY=your-ultra-secure-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
   
   # Database Configuration
   DATABASE_URL=postgresql://username:password@localhost:5432/wildquest_db
   
   # M-Pesa API Configuration
   MPESA_ENVIRONMENT=sandbox  # Change to 'production' for live
   MPESA_CONSUMER_KEY=your-mpesa-consumer-key
   MPESA_CONSUMER_SECRET=your-mpesa-consumer-secret
   MPESA_BUSINESS_SHORTCODE=your-business-shortcode
   MPESA_PASSKEY=your-mpesa-passkey
   MPESA_CALLBACK_URL=https://yourdomain.com/api/mpesa/callback/
   
   # WhatsApp Business API
   WHATSAPP_PHONE_NUMBER=+254700000000
   WHATSAPP_API_TOKEN=your-whatsapp-business-token
   WHATSAPP_WEBHOOK_VERIFY_TOKEN=your-webhook-verify-token
   
   # Email Configuration
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-specific-password
   EMAIL_USE_TLS=True
   
   # File Storage (Optional - for production)
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   AWS_STORAGE_BUCKET_NAME=wildquest-media-bucket
   ```

5. **Database Setup**
   ```bash
   # Create and apply migrations
   python manage.py makemigrations
   python manage.py migrate
   
   # Create superuser account
   python manage.py createsuperuser
   ```

6. **Load Sample Data** (Optional)
   ```bash
   python manage.py loaddata fixtures/kenya_locations.json
   python manage.py loaddata fixtures/sample_categories.json
   python manage.py loaddata fixtures/sample_events.json
   ```

7. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

**🎉 Access Points:**
- **Public Website**: http://localhost:8000
- **Admin Dashboard**: http://localhost:8000/admin
- **API Endpoints**: http://localhost:8000/api/

## 🛡️ Security & Configuration

### **Production Security Checklist**
- [ ] Set `DEBUG = False` in production
- [ ] Configure secure `SECRET_KEY`
- [ ] Enable HTTPS with SSL certificates
- [ ] Set up proper database security
- [ ] Configure CORS policies
- [ ] Enable Django security middleware
- [ ] Set up monitoring and logging
- [ ] Configure backup strategies

### **M-Pesa Integration Setup**
```python
# M-Pesa Configuration in settings.py
MPESA_CONFIG = {
    'CONSUMER_KEY': os.getenv('MPESA_CONSUMER_KEY'),
    'CONSUMER_SECRET': os.getenv('MPESA_CONSUMER_SECRET'),
    'ENVIRONMENT': os.getenv('MPESA_ENVIRONMENT', 'sandbox'),
    'BUSINESS_SHORTCODE': os.getenv('MPESA_BUSINESS_SHORTCODE'),
    'PASSKEY': os.getenv('MPESA_PASSKEY'),
    'CALLBACK_URL': os.getenv('MPESA_CALLBACK_URL'),
    'ACCOUNT_REFERENCE': 'WildQuest',
    'TRANSACTION_DESC': 'Travel Booking Payment',
}
```

## 📊 Admin Dashboard Features

### **Comprehensive Event Management**
- **Visual Event Builder**: Rich text editor with media upload capabilities
- **Pricing Strategy Tools**: Dynamic pricing with seasonal adjustments
- **Capacity Management**: Real-time availability tracking with automated notifications
- **Content Scheduling**: Publish events with scheduled availability dates

### **Advanced Booking Management**
- **Customer Relationship Dashboard**: Complete customer interaction history
- **Payment Processing Center**: M-Pesa transaction monitoring and reconciliation
- **Group Booking Tools**: Manage family and corporate group reservations
- **Communication Hub**: Integrated WhatsApp, email, and SMS notifications

### **Business Intelligence Features**
- **Revenue Analytics**: Monthly, quarterly, and annual revenue reports
- **Customer Insights**: Booking patterns and demographic analysis  
- **Popular Destinations**: Track trending locations and experiences
- **Performance Metrics**: Conversion rates and booking success analytics

## 💳 Payment System Integration

### **M-Pesa STK Push Implementation**
WildQuest leverages Safaricom's Daraja API for seamless mobile payments:

```python
# Example M-Pesa STK Push workflow
def initiate_mpesa_payment(booking):
    payload = {
        'BusinessShortCode': MPESA_SHORTCODE,
        'Password': generate_password(),
        'Timestamp': get_timestamp(),
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': booking.total_amount,
        'PartyA': booking.customer_phone,
        'PartyB': MPESA_SHORTCODE,
        'PhoneNumber': booking.customer_phone,
        'CallBackURL': MPESA_CALLBACK_URL,
        'AccountReference': f'WQ-{booking.booking_id}',
        'TransactionDesc': f'Payment for {booking.event.title}'
    }
    # Process payment request
```

### **Supported Payment Methods**
1. **M-Pesa** (Primary - 95% of Kenyan market)
2. **Bank Transfer** (Corporate bookings)
3. **Credit/Debit Cards** (International visitors)
4. **Cash Payments** (Tracked in system)

## 📱 WhatsApp Integration Workflow

### **Automated Booking Process**
1. **Customer Inquiry**: WhatsApp message received via webhook
2. **Message Processing**: AI-powered intent recognition and data extraction
3. **Admin Dashboard**: Booking request appears in admin interface
4. **Conversion**: Admin converts WhatsApp inquiry to formal booking
5. **Payment Link**: Automated M-Pesa payment link sent via WhatsApp

### **Sample WhatsApp Message Format**
```
Hi WildQuest! 

I'm interested in the Maasai Mara Safari package for 4 people from March 15-18, 2024.

Details:
- Name: Jane Wanjiku
- Phone: +254722123456
- Adults: 2, Children: 2
- Special requests: Vegetarian meals

Please send booking details and payment information.
```

## 🌍 Kenya Tourism Coverage

### **Regional Destinations**
| Region | Key Destinations | Experience Types |
|--------|------------------|------------------|
| **Coast** | Diani, Watamu, Malindi, Lamu | Beach holidays, water sports, cultural tours |
| **Rift Valley** | Maasai Mara, Nakuru, Hell's Gate | Wildlife safaris, hot air balloons, hiking |
| **Central** | Mount Kenya, Aberdares, Ol Pejeta | Mountain climbing, conservancy visits |
| **Western** | Kakamega Forest, Lake Victoria | Forest walks, fishing, cultural experiences |
| **Northern** | Samburu, Turkana, Marsabit | Cultural tourism, desert expeditions |

### **Cultural Integration Features**
- **Multi-language Support**: English and Kiswahili interfaces
- **Local Holiday Calendar**: Integration with Kenyan public holidays
- **Cultural Sensitivity**: Respectful representation of local communities
- **Regional Customization**: Location-specific content and recommendations

## 🔧 API Documentation

### **Core API Endpoints**
```bash
# Event Management
GET    /api/events/                 # List all events
GET    /api/events/{id}/           # Event details
POST   /api/events/               # Create event (admin)
PUT    /api/events/{id}/          # Update event (admin)

# Booking System
POST   /api/bookings/             # Create booking
GET    /api/bookings/{id}/        # Booking details
PUT    /api/bookings/{id}/        # Update booking

# Payment Processing
POST   /api/payments/mpesa/       # Initiate M-Pesa payment
POST   /api/payments/callback/    # M-Pesa callback handler

# WhatsApp Integration
POST   /api/whatsapp/webhook/     # WhatsApp message webhook
GET    /api/whatsapp/requests/    # List WhatsApp requests

# Location Services
GET    /api/locations/            # Kenya locations
GET    /api/locations/counties/   # List counties
GET    /api/locations/regions/    # List regions
```

### **Authentication & Permissions**
- **Public Endpoints**: Event listings, location data
- **Customer Endpoints**: Booking creation, payment initiation
- **Admin Endpoints**: Full CRUD operations with Django authentication

## 🚀 Deployment Guide

### **Recommended Production Stack**
- **Web Server**: Nginx (reverse proxy & static files)
- **Application Server**: Gunicorn with multiple workers
- **Database**: PostgreSQL with connection pooling
- **Caching**: Redis for session and query caching
- **Task Queue**: Celery with Redis broker
- **Monitoring**: Sentry for error tracking
- **File Storage**: AWS S3 or local storage with CDN

### **Production Deployment Steps**
```bash
# 1. Server Setup (Ubuntu 20.04 LTS)
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx postgresql redis-server

# 2. Application Deployment
git clone https://github.com/steveongera/wildquest.git
cd wildquest
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Database Setup
sudo -u postgres createdb wildquest_prod
python manage.py migrate
python manage.py collectstatic

# 4. Nginx Configuration
sudo cp deployment/nginx.conf /etc/nginx/sites-available/wildquest
sudo ln -s /etc/nginx/sites-available/wildquest /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# 5. Systemd Service
sudo cp deployment/wildquest.service /etc/systemd/system/
sudo systemctl enable wildquest
sudo systemctl start wildquest
```

## 📈 Performance Optimization

### **Database Optimization**
- **Indexing Strategy**: Strategic indexes on frequently queried fields
- **Query Optimization**: Select_related and prefetch_related usage
- **Connection Pooling**: PgBouncer for PostgreSQL connections
- **Read Replicas**: Separate read/write database instances

### **Caching Strategy**
- **Template Caching**: Cache rendered templates for anonymous users
- **Query Caching**: Redis-based query result caching
- **Static Files**: CDN integration for media files
- **API Responses**: Cache API responses with appropriate TTL

### **Monitoring & Analytics**
```python
# Custom metrics tracking
LOGGING = {
    'version': 1,
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'sentry_sdk.integrations.logging.SentryHandler',
        },
        'booking_analytics': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/wildquest/bookings.log',
        }
    }
}
```

## 🧪 Testing Strategy

### **Test Coverage**
```bash
# Run complete test suite
python manage.py test

# Coverage report
coverage run --source='.' manage.py test
coverage report -m
coverage html  # Generate HTML coverage report
```

### **Testing Categories**
- **Unit Tests**: Model validation, utility functions
- **Integration Tests**: API endpoints, payment flows
- **Functional Tests**: User booking journey, admin workflows
- **Performance Tests**: Load testing for high-traffic scenarios

## 🤝 Contributing to WildQuest

WildQuest welcomes contributions from the developer community! Here's how to get involved:

### **Development Workflow**
1. **Fork the repository** on GitHub
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** with appropriate tests
4. **Run the test suite** to ensure nothing breaks
5. **Commit your changes** (`git commit -m 'Add amazing feature'`)
6. **Push to your branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request** with detailed description

### **Contribution Guidelines**
- **Code Style**: Follow PEP 8 and Django best practices
- **Documentation**: Update README and docstrings for new features
- **Testing**: Write tests for new functionality
- **Commit Messages**: Use clear, descriptive commit messages
- **Issue Tracking**: Link PRs to relevant GitHub issues

### **Priority Areas for Contribution**
- 🌐 **Internationalization**: Additional language support
- 📱 **Mobile App**: React Native or Flutter mobile app
- 🤖 **AI Integration**: Chatbot for customer service
- 🔐 **Security Enhancements**: Advanced security features
- 📊 **Analytics Dashboard**: Enhanced reporting capabilities

## 🐛 Troubleshooting Guide

### **Common Issues & Solutions**

**M-Pesa Integration Issues**
```bash
# Check M-Pesa credentials
python manage.py shell
>>> from django.conf import settings
>>> print(settings.MPESA_CONFIG)

# Test M-Pesa connection
python manage.py test_mpesa_connection
```

**WhatsApp Webhook Problems**
```bash
# Verify webhook URL is accessible
curl -X POST https://yourdomain.com/api/whatsapp/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"test": "message"}'

# Check webhook logs
tail -f /var/log/wildquest/whatsapp.log
```

**Database Connection Issues**
```bash
# Test database connection
python manage.py dbshell

# Check migration status
python manage.py showmigrations
```

## 📞 Support & Community

### **Getting Help**
- **📧 Technical Support**: steve.ongera@wildquest.co.ke
- **💬 Community Discord**: [Join our community](https://discord.gg/wildquest)
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/steveongera/wildquest/issues)
- **📚 Documentation**: [Wiki Pages](https://github.com/steveongera/wildquest/wiki)

### **Business Inquiries**
- **🏢 Partnership Opportunities**: partnerships@wildquest.co.ke
- **💼 Enterprise Solutions**: enterprise@wildquest.co.ke
- **📈 White Label Solutions**: licensing@wildquest.co.ke

## 👨‍💻 About the Developer

**Steve Ongera** is a passionate full-stack developer and entrepreneur based in Kenya, with extensive experience in building scalable web applications for the East African market. With deep understanding of local business needs and technical challenges, Steve has crafted WildQuest to address the specific requirements of Kenya's tourism industry.

### **Connect with Steve**
- **🌐 Portfolio**: [steveongera.com](https://steveongera.com)
- **💼 LinkedIn**: [linkedin.com/in/steveongera](https://linkedin.com/in/steveongera)
- **🐱 GitHub**: [github.com/steveongera](https://github.com/steveongera)
- **🐦 Twitter**: [@steveongera](https://twitter.com/steveongera)
- **📧 Email**: steve.ongera@gmail.com

## 📄 License & Legal

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for full details.

### **Third-Party Acknowledgments**
- **Safaricom Limited** for M-Pesa Daraja API access
- **Kenya Tourism Board** for destination data and imagery
- **Django Software Foundation** for the excellent web framework
- **PostgreSQL Global Development Group** for robust database technology
- **Open Source Community** for various libraries and tools

### **Disclaimer**
WildQuest is an independent software project and is not officially affiliated with any tourism board or government entity. All destination information is provided for reference purposes and should be verified independently.

---

## 🌟 Star History

If you find WildQuest useful for your travel business or learning journey, please consider giving it a star on GitHub!

[![Star History Chart](https://api.star-history.com/svg?repos=steveongera/wildquest&type=Date)](https://star-history.com/#steveongera/wildquest&Date)

---

**🇰🇪 WildQuest - Discover Kenya's Wild Beauty**

*Built with ❤️ in Kenya by Steve Ongera*

---

*© 2025 Steve Ongera. All rights reserved. WildQuest is a trademark of Steve Ongera.*