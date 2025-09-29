from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid
from django.utils.text import slugify

class SEOMixin(models.Model):
    """Reusable SEO fields for any model"""
    meta_title = models.CharField(max_length=60, blank=True, help_text="60 characters max")
    meta_description = models.CharField(max_length=160, blank=True, help_text="160 characters max")
    meta_keywords = models.CharField(max_length=255, blank=True)
    og_image = models.ImageField(upload_to='seo/', blank=True, help_text="1200x630px recommended")
    
    class Meta:
        abstract = True


class Category(models.Model):
    """Categories for different types of events/experiences"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Font awesome icon class
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Location(models.Model):
    """Kenyan locations and destinations"""
    name = models.CharField(max_length=100)
    county = models.CharField(max_length=50)
    region = models.CharField(max_length=50)  # Coast, Central, Western, etc.
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    description = models.TextField(blank=True)
    is_popular = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name}, {self.county}"

class Event(models.Model):
    """Main event/experience model"""
    EVENT_TYPES = [
        ('safari', 'Safari'),
        ('beach', 'Beach Holiday'),
        ('mountain', 'Mountain Climbing'),
        ('cultural', 'Cultural Experience'),
        ('adventure', 'Adventure Sports'),
        ('road_trip', 'Road Trip'),
        ('summit', 'Summit'),
        ('conference', 'Conference'),
        ('retreat', 'Retreat'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    
    # Event scheduling
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    duration_days = models.PositiveIntegerField()
    
    # Capacity management
    max_participants = models.PositiveIntegerField()
    min_participants = models.PositiveIntegerField(default=1)
    current_bookings = models.PositiveIntegerField(default=0)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    child_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vip_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    group_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Features and inclusions
    includes = models.TextField(help_text="What's included in the package")
    excludes = models.TextField(blank=True, help_text="What's not included")
    requirements = models.TextField(blank=True, help_text="Requirements for participants")
    
    # Booking settings
    booking_deadline = models.DateTimeField()
    cancellation_policy = models.TextField()
    whatsapp_booking = models.BooleanField(default=True)
    online_payment = models.BooleanField(default=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    featured = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = f"{self.title} - WildQuest Kenya"
        if not self.meta_description:
            self.meta_description = self.description[:155] + "..."
        super().save(*args, **kwargs)
    
    def get_schema_markup(self):
        """Generate JSON-LD structured data"""
        return {
            "@context": "https://schema.org",
            "@type": "TouristAttraction",
            "name": self.title,
            "description": self.description,
            "image": self.og_image.url if self.og_image else "",
            "offers": {
                "@type": "Offer",
                "price": str(self.base_price),
                "priceCurrency": "KES"
            },
            "location": {
                "@type": "Place",
                "name": self.location,
                "address": {
                    "@type": "PostalAddress",
                    "addressCountry": "KE"
                }
            }
        }
    
    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return self.title
    
    @property
    def available_spots(self):
        return self.max_participants - self.current_bookings
    
    @property
    def is_fully_booked(self):
        return self.current_bookings >= self.max_participants
    
    @property
    def is_booking_open(self):
        return (
            self.status == 'published' and 
            timezone.now() < self.booking_deadline and
            not self.is_fully_booked
        )

class EventImage(models.Model):
    """Images for events"""
    event = models.ForeignKey(Event, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='events/%Y/%m/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.event.title}"

class PricingTier(models.Model):
    """Different pricing tiers for VIP, Regular, etc."""
    TIER_TYPES = [
        ('regular', 'Regular'),
        ('vip', 'VIP'),
        ('premium', 'Premium'),
        ('budget', 'Budget'),
    ]
    
    event = models.ForeignKey(Event, related_name='pricing_tiers', on_delete=models.CASCADE)
    tier_type = models.CharField(max_length=20, choices=TIER_TYPES)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_capacity = models.PositiveIntegerField()
    current_bookings = models.PositiveIntegerField(default=0)
    features = models.TextField()  # JSON or comma-separated features
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['event', 'tier_type']
    
    def __str__(self):
        return f"{self.event.title} - {self.name}"
    
    @property
    def available_spots(self):
        return self.max_capacity - self.current_bookings

class Booking(models.Model):
    """Main booking model for event tickets"""
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    BOOKING_METHODS = [
        ('whatsapp', 'WhatsApp'),
        ('online', 'Online'),
        ('phone', 'Phone'),
        ('email', 'Email'),
    ]
    
    booking_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    pricing_tier = models.ForeignKey(PricingTier, on_delete=models.CASCADE, null=True, blank=True)
    
    # Customer information (no account required)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    # Booking details
    number_of_participants = models.PositiveIntegerField()
    adults_count = models.PositiveIntegerField(default=1)
    children_count = models.PositiveIntegerField(default=0)
    
    # Pricing breakdown
    base_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Booking metadata
    booking_method = models.CharField(max_length=20, choices=BOOKING_METHODS)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    special_requests = models.TextField(blank=True)
    dietary_requirements = models.TextField(blank=True)
    
    # System fields
    booked_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # User account (optional)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.customer_name}"
    
    class Meta:
        ordering = ['-booked_at']

class BookingParticipant(models.Model):
    """Individual participants in a booking"""
    PARTICIPANT_TYPES = [
        ('adult', 'Adult'),
        ('child', 'Child'),
        ('infant', 'Infant'),
    ]
    
    booking = models.ForeignKey(Booking, related_name='participants', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(null=True, blank=True)
    participant_type = models.CharField(max_length=10, choices=PARTICIPANT_TYPES)
    id_number = models.CharField(max_length=20, blank=True)
    passport_number = models.CharField(max_length=20, blank=True)
    medical_conditions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.booking.booking_id}"

class Payment(models.Model):
    """Payment tracking for bookings"""
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    booking = models.ForeignKey(Booking, related_name='payments', on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # M-Pesa specific fields
    mpesa_checkout_id = models.CharField(max_length=100, blank=True)
    mpesa_transaction_id = models.CharField(max_length=100, blank=True)
    mpesa_phone_number = models.CharField(max_length=15, blank=True)
    
    # Transaction details
    transaction_reference = models.CharField(max_length=100, blank=True)
    gateway_response = models.TextField(blank=True)  # Store raw gateway response
    failure_reason = models.TextField(blank=True)
    
    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount}"
    
    class Meta:
        ordering = ['-initiated_at']

class WhatsAppBooking(models.Model):
    """Track WhatsApp booking requests"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    message = models.TextField()
    participants_count = models.PositiveIntegerField()
    status = models.CharField(max_length=20, default='new')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Link to actual booking when processed
    booking = models.OneToOneField(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"WhatsApp booking - {self.customer_name} for {self.event.title}"

class Review(models.Model):
    """Customer reviews for events"""
    event = models.ForeignKey(Event, related_name='reviews', on_delete=models.CASCADE)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, null=True, blank=True)
    
    reviewer_name = models.CharField(max_length=100)
    reviewer_email = models.EmailField(blank=True)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    # Review metadata
    is_verified = models.BooleanField(default=False)  # Verified if linked to booking
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.reviewer_name} for {self.event.title}"

class FAQ(models.Model):
    """Frequently asked questions for events"""
    event = models.ForeignKey(Event, related_name='faqs', on_delete=models.CASCADE)
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.question

class Itinerary(models.Model):
    """Day-by-day itinerary for events"""
    event = models.ForeignKey(Event, related_name='itinerary', on_delete=models.CASCADE)
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    activities = models.TextField()
    meals_included = models.CharField(max_length=100, blank=True)  # B, L, D
    accommodation = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['day_number']
        unique_together = ['event', 'day_number']
    
    def __str__(self):
        return f"Day {self.day_number}: {self.title}"

class EventFeature(models.Model):
    """Features and amenities for events"""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class EventFeatureAssignment(models.Model):
    """Many-to-many relationship between events and features"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    feature = models.ForeignKey(EventFeature, on_delete=models.CASCADE)
    is_included = models.BooleanField(default=True)
    notes = models.CharField(max_length=200, blank=True)
    
    class Meta:
        unique_together = ['event', 'feature']

class NewsletterSubscription(models.Model):
    """Newsletter subscriptions"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

class ContactInquiry(models.Model):
    """Contact form submissions"""
    INQUIRY_TYPES = [
        ('general', 'General Inquiry'),
        ('booking', 'Booking Question'),
        ('support', 'Support Request'),
        ('partnership', 'Partnership'),
        ('feedback', 'Feedback'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status tracking
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Inquiry from {self.name} - {self.subject}"

class SystemConfiguration(models.Model):
    """System-wide configuration settings"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.key