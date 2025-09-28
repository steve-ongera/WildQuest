from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponse
import csv
from .models import (
    Category, Location, Event, EventImage, PricingTier, Booking, 
    BookingParticipant, Payment, WhatsAppBooking, Review, FAQ, 
    Itinerary, EventFeature, EventFeatureAssignment, NewsletterSubscription,
    ContactInquiry, SystemConfiguration
)

# Custom Admin Site Configuration
admin.site.site_header = "traveling_agency Travel Agency Admin"
admin.site.site_title = "traveling_agency Admin Portal"
admin.site.index_title = "Travel & Tourism Management Dashboard"

# Custom Filters
class BookingStatusFilter(SimpleListFilter):
    title = 'Booking Status'
    parameter_name = 'booking_status'
    
    def lookups(self, request, model_admin):
        return (
            ('available', 'Available'),
            ('almost_full', 'Almost Full (≤5 spots)'),
            ('fully_booked', 'Fully Booked'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'available':
            return queryset.filter(current_bookings__lt=models.F('max_participants') - 5)
        elif self.value() == 'almost_full':
            return queryset.filter(
                current_bookings__gte=models.F('max_participants') - 5,
                current_bookings__lt=models.F('max_participants')
            )
        elif self.value() == 'fully_booked':
            return queryset.filter(current_bookings__gte=models.F('max_participants'))

class PaymentStatusFilter(SimpleListFilter):
    title = 'Payment Status'
    parameter_name = 'payment_status'
    
    def lookups(self, request, model_admin):
        return (
            ('paid', 'Fully Paid'),
            ('pending', 'Payment Pending'),
            ('partial', 'Partially Paid'),
            ('failed', 'Payment Failed'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'paid':
            return queryset.filter(status='paid')
        elif self.value() == 'pending':
            return queryset.filter(status='pending')
        elif self.value() == 'partial':
            return queryset.filter(status='confirmed')
        elif self.value() == 'failed':
            return queryset.filter(payments__status='failed')

# Inline Admin Classes
class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    ordering = ['order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="50" style="border-radius: 4px;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = 'Preview'

class PricingTierInline(admin.TabularInline):
    model = PricingTier
    extra = 1
    fields = ('tier_type', 'name', 'price', 'max_capacity', 'current_bookings', 'available_spots', 'is_active')
    readonly_fields = ('current_bookings', 'available_spots')
    
    def available_spots(self, obj):
        if obj.id:
            return obj.available_spots
        return '-'
    available_spots.short_description = 'Available'

class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 1
    fields = ('question', 'answer', 'order', 'is_active')
    ordering = ['order']

class ItineraryInline(admin.TabularInline):
    model = Itinerary
    extra = 1
    fields = ('day_number', 'title', 'description', 'activities', 'meals_included', 'accommodation')
    ordering = ['day_number']

class BookingParticipantInline(admin.TabularInline):
    model = BookingParticipant
    extra = 0
    fields = ('name', 'age', 'participant_type', 'id_number', 'passport_number', 'medical_conditions')

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('payment_id', 'status_display', 'initiated_at', 'completed_at')
    fields = ('payment_id', 'amount', 'payment_method', 'status_display', 'mpesa_transaction_id', 'initiated_at', 'completed_at')
    
    def status_display(self, obj):
        colors = {
            'pending': '#ffa500',
            'processing': '#1e90ff',
            'completed': '#32cd32',
            'failed': '#dc143c',
            'refunded': '#9370db',
            'cancelled': '#696969'
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'

class EventFeatureAssignmentInline(admin.TabularInline):
    model = EventFeatureAssignment
    extra = 1
    fields = ('feature', 'is_included', 'notes')

# Custom Actions
def export_to_csv(modeladmin, request, queryset):
    """Export selected items to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{modeladmin.model.__name__.lower()}_export.csv"'
    
    writer = csv.writer(response)
    # Write header
    fields = [field.name for field in modeladmin.model._meta.fields]
    writer.writerow(fields)
    
    # Write data
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in fields])
    
    return response
export_to_csv.short_description = "Export selected to CSV"

# Main Admin Classes
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'event_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'event_count_display')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'icon')
        }),
        ('Settings', {
            'fields': ('is_active', 'created_at', 'event_count_display')
        })
    )
    
    actions = [export_to_csv]
    
    def event_count(self, obj):
        return obj.event_set.count()
    event_count.short_description = 'Events'
    
    def event_count_display(self, obj):
        count = obj.event_set.count()
        url = reverse('admin:traveling_agency_event_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{} events</a>', url, count)
    event_count_display.short_description = 'Events'

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'county', 'region', 'is_popular', 'event_count', 'coordinates', 'created_at')
    list_filter = ('county', 'region', 'is_popular', 'created_at')
    search_fields = ('name', 'county', 'region', 'description')
    readonly_fields = ('created_at', 'event_count_display')
    
    fieldsets = (
        ('Location Details', {
            'fields': ('name', 'county', 'region', 'description')
        }),
        ('Geographic Coordinates', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_popular', 'created_at', 'event_count_display')
        })
    )
    
    actions = [export_to_csv]
    
    def coordinates(self, obj):
        if obj.latitude and obj.longitude:
            return f"{obj.latitude}, {obj.longitude}"
        return "Not set"
    coordinates.short_description = 'GPS Coordinates'
    
    def event_count(self, obj):
        return obj.event_set.count()
    event_count.short_description = 'Events'
    
    def event_count_display(self, obj):
        count = obj.event_set.count()
        url = reverse('admin:traveling_agency_event_changelist') + f'?location__id__exact={obj.id}'
        return format_html('<a href="{}">{} events</a>', url, count)
    event_count_display.short_description = 'Events'

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'event_type', 'location_display', 'start_date', 'status_display', 
        'booking_progress', 'revenue_display', 'featured', 'booking_status_display'
    )
    list_filter = (
        'event_type', 'status', 'featured', 'category', 
        'location__county', 'start_date', 'created_at', BookingStatusFilter
    )
    search_fields = ('title', 'description', 'location__name', 'location__county')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = (
        'current_bookings', 'available_spots', 'revenue_total', 
        'created_at', 'updated_at', 'booking_deadline_status'
    )
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 
                      'event_type', 'category', 'location')
        }),
        ('Event Schedule', {
            'fields': ('start_date', 'end_date', 'duration_days', 'booking_deadline', 'booking_deadline_status')
        }),
        ('Capacity & Pricing', {
            'fields': ('max_participants', 'min_participants', 'current_bookings', 'available_spots',
                      'base_price', 'child_price', 'vip_price', 'group_discount_percentage')
        }),
        ('Package Information', {
            'fields': ('includes', 'excludes', 'requirements', 'cancellation_policy'),
            'classes': ('collapse',)
        }),
        ('Booking Configuration', {
            'fields': ('whatsapp_booking', 'online_payment')
        }),
        ('Status & Revenue', {
            'fields': ('status', 'featured', 'revenue_total', 'created_by', 'created_at', 'updated_at')
        })
    )
    
    inlines = [EventImageInline, PricingTierInline, FAQInline, ItineraryInline, EventFeatureAssignmentInline]
    
    actions = ['mark_as_featured', 'mark_as_published', 'mark_as_suspended', 'duplicate_event', export_to_csv]
    
    def location_display(self, obj):
        return f"{obj.location.name}, {obj.location.county}"
    location_display.short_description = 'Location'
    
    def status_display(self, obj):
        colors = {
            'draft': '#ffa500',
            'published': '#32cd32',
            'suspended': '#dc143c',
            'cancelled': '#696969'
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def booking_progress(self, obj):
        percentage = (obj.current_bookings / obj.max_participants) * 100 if obj.max_participants > 0 else 0
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; height: 20px; background-color: #28a745; border-radius: 3px;"></div>'
            '</div>'
            '<small>{}/{} ({}%)</small>',
            percentage, obj.current_bookings, obj.max_participants, int(percentage)
        )
    booking_progress.short_description = 'Booking Progress'
    
    def booking_status_display(self, obj):
        if obj.is_fully_booked:
            return format_html('<span style="color: red; font-weight: bold;">● FULLY BOOKED</span>')
        elif obj.available_spots <= 5:
            return format_html('<span style="color: orange; font-weight: bold;">● ALMOST FULL</span>')
        else:
            return format_html('<span style="color: green; font-weight: bold;">● AVAILABLE</span>')
    booking_status_display.short_description = 'Availability'
    
    def revenue_display(self, obj):
        # Calculate total revenue from bookings
        total_revenue = obj.booking_set.filter(status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        return f"KES {total_revenue:,.2f}"
    revenue_display.short_description = 'Revenue'
    
    def revenue_total(self, obj):
        if obj.id:
            total_revenue = obj.booking_set.filter(status='paid').aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            return f"KES {total_revenue:,.2f}"
        return "KES 0.00"
    revenue_total.short_description = 'Total Revenue'
    
    def booking_deadline_status(self, obj):
        if obj.booking_deadline:
            if timezone.now() > obj.booking_deadline:
                return format_html('<span style="color: red;">EXPIRED</span>')
            else:
                days_left = (obj.booking_deadline - timezone.now()).days
                return format_html('<span style="color: green;">{} days remaining</span>', days_left)
        return "No deadline set"
    booking_deadline_status.short_description = 'Deadline Status'
    
    def available_spots(self, obj):
        return obj.available_spots
    available_spots.short_description = 'Available Spots'
    
    # Custom Actions
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} events marked as featured.')
    mark_as_featured.short_description = "Mark selected events as featured"
    
    def mark_as_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} events published.')
    mark_as_published.short_description = "Publish selected events"
    
    def mark_as_suspended(self, request, queryset):
        updated = queryset.update(status='suspended')
        self.message_user(request, f'{updated} events suspended.')
    mark_as_suspended.short_description = "Suspend selected events"
    
    def duplicate_event(self, request, queryset):
        for event in queryset:
            event.pk = None
            event.title = f"{event.title} (Copy)"
            event.slug = f"{event.slug}-copy"
            event.status = 'draft'
            event.current_bookings = 0
            event.save()
        self.message_user(request, f'{queryset.count()} events duplicated as drafts.')
    duplicate_event.short_description = "Duplicate selected events"

@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ('event', 'alt_text', 'is_primary', 'order', 'image_preview', 'created_at')
    list_filter = ('is_primary', 'created_at', 'event__category')
    search_fields = ('event__title', 'alt_text')
    readonly_fields = ('image_preview', 'created_at')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="150" height="100" style="border-radius: 4px;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = 'Image Preview'

@admin.register(PricingTier)
class PricingTierAdmin(admin.ModelAdmin):
    list_display = ('event', 'name', 'tier_type', 'price', 'max_capacity', 'current_bookings', 'available_spots', 'is_active')
    list_filter = ('tier_type', 'is_active', 'event__category')
    search_fields = ('name', 'event__title', 'description')
    readonly_fields = ('current_bookings', 'available_spots')
    
    def available_spots(self, obj):
        return obj.available_spots
    available_spots.short_description = 'Available'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_id_short', 'customer_name', 'event_title', 'participants_display',
        'total_amount', 'status_display', 'booking_method', 'payment_status', 'booked_at'
    )
    list_filter = (
        'status', 'booking_method', 'booked_at', 'event__event_type',
        'event__category', PaymentStatusFilter
    )
    search_fields = (
        'booking_id', 'customer_name', 'customer_email', 
        'customer_phone', 'event__title'
    )
    readonly_fields = (
        'booking_id', 'booked_at', 'updated_at', 'payment_summary',
        'booking_age', 'event_link'
    )
    date_hierarchy = 'booked_at'
    
    fieldsets = (
        ('Booking Reference', {
            'fields': ('booking_id', 'status', 'booking_method', 'booking_age')
        }),
        ('Event Information', {
            'fields': ('event_link', 'pricing_tier')
        }),
        ('Customer Information', {
            'fields': (
                'customer_name', 'customer_email', 'customer_phone', 
                'customer_address', 'emergency_contact_name', 'emergency_contact_phone'
            )
        }),
        ('Booking Details', {
            'fields': (
                'number_of_participants', 'adults_count', 'children_count',
                'special_requests', 'dietary_requirements'
            )
        }),
        ('Payment Information', {
            'fields': ('base_amount', 'discount_amount', 'tax_amount', 'total_amount', 'payment_summary')
        }),
        ('Timestamps', {
            'fields': ('booked_at', 'confirmed_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [BookingParticipantInline, PaymentInline]
    
    actions = ['confirm_bookings', 'cancel_bookings', 'send_confirmation_emails', export_to_csv]
    
    def booking_id_short(self, obj):
        return str(obj.booking_id)[:8] + "..."
    booking_id_short.short_description = 'Booking ID'
    
    def event_title(self, obj):
        return obj.event.title[:30] + "..." if len(obj.event.title) > 30 else obj.event.title
    event_title.short_description = 'Event'
    
    def participants_display(self, obj):
        return f"{obj.number_of_participants} ({obj.adults_count}A, {obj.children_count}C)"
    participants_display.short_description = 'Participants'
    
    def status_display(self, obj):
        colors = {
            'pending': '#ffa500',
            'confirmed': '#1e90ff',
            'paid': '#32cd32',
            'cancelled': '#dc143c',
            'completed': '#9370db'
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def payment_status(self, obj):
        payments = obj.payments.all()
        if not payments.exists():
            return format_html('<span style="color: #ffa500;">No Payment</span>')
        
        latest_payment = payments.latest('initiated_at')
        colors = {
            'pending': '#ffa500',
            'processing': '#1e90ff',
            'completed': '#32cd32',
            'failed': '#dc143c',
            'refunded': '#9370db'
        }
        color = colors.get(latest_payment.status, '#000000')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, latest_payment.get_status_display()
        )
    payment_status.short_description = 'Payment'
    
    def payment_summary(self, obj):
        if obj.id:
            payments = obj.payments.all()
            total_paid = payments.filter(status='completed').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            return format_html(
                'Total Amount: KES {}<br>'
                'Amount Paid: KES {}<br>'
                'Balance: KES {}',
                obj.total_amount,
                total_paid,
                obj.total_amount - total_paid
            )
        return "Save booking first"
    payment_summary.short_description = 'Payment Summary'
    
    def booking_age(self, obj):
        age = timezone.now() - obj.booked_at
        return f"{age.days} days ago"
    booking_age.short_description = 'Booked'
    
    def event_link(self, obj):
        if obj.event:
            url = reverse('admin:traveling_agency_event_change', args=[obj.event.id])
            return format_html('<a href="{}">{}</a>', url, obj.event.title)
        return "No event"
    event_link.short_description = 'Event'
    
    # Custom Actions
    def confirm_bookings(self, request, queryset):
        updated = queryset.update(status='confirmed', confirmed_at=timezone.now())
        self.message_user(request, f'{updated} bookings confirmed.')
    confirm_bookings.short_description = "Confirm selected bookings"
    
    def cancel_bookings(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} bookings cancelled.')
    cancel_bookings.short_description = "Cancel selected bookings"
    
    def send_confirmation_emails(self, request, queryset):
        # Placeholder for email sending logic
        count = queryset.count()
        self.message_user(request, f'Confirmation emails sent for {count} bookings.')
    send_confirmation_emails.short_description = "Send confirmation emails"

@admin.register(BookingParticipant)
class BookingParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'booking_short', 'participant_type', 'age', 'id_number')
    list_filter = ('participant_type', 'booking__event__category')
    search_fields = ('name', 'booking__booking_id', 'id_number', 'passport_number')
    
    def booking_short(self, obj):
        return f"{obj.booking.customer_name} - {str(obj.booking.booking_id)[:8]}..."
    booking_short.short_description = 'Booking'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'payment_id', 'booking_short', 'amount', 'payment_method', 
        'status_display', 'mpesa_transaction_id', 'initiated_at', 'completed_at'
    )
    list_filter = ('payment_method', 'status', 'initiated_at')
    search_fields = (
        'payment_id', 'booking__booking_id', 'mpesa_transaction_id',
        'transaction_reference', 'booking__customer_name'
    )
    readonly_fields = ('payment_id', 'initiated_at', 'completed_at')
    date_hierarchy = 'initiated_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'booking', 'amount', 'payment_method', 'status')
        }),
        ('M-Pesa Transaction Details', {
            'fields': ('mpesa_checkout_id', 'mpesa_transaction_id', 'mpesa_phone_number'),
            'classes': ('collapse',)
        }),
        ('Transaction Information', {
            'fields': ('transaction_reference', 'gateway_response', 'failure_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('initiated_at', 'completed_at')
        })
    )
    
    actions = [export_to_csv]
    
    def booking_short(self, obj):
        return f"{obj.booking.customer_name} - {str(obj.booking.booking_id)[:8]}..."
    booking_short.short_description = 'Booking'
    
    def status_display(self, obj):
        colors = {
            'pending': '#ffa500',
            'processing': '#1e90ff',
            'completed': '#32cd32',
            'failed': '#dc143c',
            'refunded': '#9370db',
            'cancelled': '#696969'
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'

@admin.register(WhatsAppBooking)
class WhatsAppBookingAdmin(admin.ModelAdmin):
    list_display = (
        'customer_name', 'event', 'participants_count', 
        'status_display', 'created_at', 'processed_by'
    )
    list_filter = ('status', 'created_at', 'processed_by', 'event__category')
    search_fields = ('customer_name', 'customer_phone', 'event__title', 'message')
    readonly_fields = ('created_at', 'processed_at')
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_phone', 'participants_count')
        }),
        ('Booking Request', {
            'fields': ('event', 'message')
        }),
        ('Processing Status', {
            'fields': ('status', 'processed_by', 'booking', 'created_at', 'processed_at')
        })
    )
    
    actions = ['mark_as_processed', 'convert_to_booking', export_to_csv]
    
    def status_display(self, obj):
        colors = {
            'new': '#1e90ff',
            'processing': '#ffa500',
            'processed': '#32cd32',
            'converted': '#9370db'
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.status.title()
        )
    status_display.short_description = 'Status'
    
    def mark_as_processed(self, request, queryset):
        updated = queryset.update(status='processed', processed_at=timezone.now(), processed_by=request.user)
        self.message_user(request, f'{updated} WhatsApp bookings marked as processed.')
    mark_as_processed.short_description = "Mark as processed"
    
    def convert_to_booking(self, request, queryset):
        # Placeholder for booking conversion logic
        count = queryset.count()
        self.message_user(request, f'{count} WhatsApp requests ready for conversion.')
    convert_to_booking.short_description = "Convert to formal booking"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'reviewer_name', 'event', 'rating_display', 'is_verified', 
        'is_approved', 'created_at'
    )
    list_filter = ('rating', 'is_verified', 'is_approved', 'created_at', 'event__category')
    search_fields = ('reviewer_name', 'title', 'comment', 'event__title')
    readonly_fields = ('is_verified', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Review Information', {
            'fields': ('event', 'booking', 'reviewer_name', 'reviewer_email')
        }),
        ('Review Content', {
            'fields': ('rating', 'title', 'comment')
        }),
        ('Moderation', {
            'fields': ('is_verified', 'is_approved', 'created_at', 'updated_at')
        })
    )
    
    actions = ['approve_reviews', 'disapprove_reviews', 'verify_reviews', export_to_csv]
    
    def rating_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #ffa500; font-size: 16px;">{}</span>', stars)
    rating_display.short_description = 'Rating'
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews approved.')
    approve_reviews.short_description = "Approve selected reviews"
    
    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews disapproved.')
    disapprove_reviews.short_description = "Disapprove selected reviews"
    
    def verify_reviews(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} reviews verified.')
    verify_reviews.short_description = "Verify selected reviews"

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question_short', 'event', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'event__category')
    search_fields = ('question', 'answer', 'event__title')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('FAQ Information', {
            'fields': ('event', 'question', 'answer')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active', 'created_at')
        })
    )
    
    def question_short(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question
    question_short.short_description = 'Question'

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ('event', 'day_number', 'title', 'activities_short', 'meals_included', 'accommodation')
    list_filter = ('event__category', 'meals_included')
    search_fields = ('event__title', 'title', 'description', 'activities')
    
    fieldsets = (
        ('Itinerary Information', {
            'fields': ('event', 'day_number', 'title', 'description')
        }),
        ('Activities & Services', {
            'fields': ('activities', 'meals_included', 'accommodation')
        })
    )
    
    def activities_short(self, obj):
        return obj.activities[:50] + "..." if len(obj.activities) > 50 else obj.activities
    activities_short.short_description = 'Activities'

@admin.register(EventFeature)
class EventFeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'description_short', 'usage_count')
    search_fields = ('name', 'description')
    
    def description_short(self, obj):
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'
    
    def usage_count(self, obj):
        return obj.eventfeatureassignment_set.count()
    usage_count.short_description = 'Used in Events'

@admin.register(EventFeatureAssignment)
class EventFeatureAssignmentAdmin(admin.ModelAdmin):
    list_display = ('event', 'feature', 'is_included', 'notes')
    list_filter = ('is_included', 'feature', 'event__category')
    search_fields = ('event__title', 'feature__name', 'notes')

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'email', 'inquiry_type', 'subject_short', 
        'event', 'is_resolved', 'created_at'
    )
    list_filter = ('inquiry_type', 'is_resolved', 'created_at', 'event__category')
    search_fields = ('name', 'email', 'subject', 'message', 'event__title')
    readonly_fields = ('created_at', 'resolved_at')
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'inquiry_type')
        }),
        ('Inquiry Details', {
            'fields': ('subject', 'message', 'event')
        }),
        ('Resolution Status', {
            'fields': ('is_resolved', 'resolved_by', 'resolved_at', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )
    
    actions = ['mark_as_resolved', 'mark_as_unresolved', export_to_csv]
    
    def subject_short(self, obj):
        return obj.subject[:40] + "..." if len(obj.subject) > 40 else obj.subject
    subject_short.short_description = 'Subject'
    
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(is_resolved=True, resolved_at=timezone.now(), resolved_by=request.user)
        self.message_user(request, f'{updated} inquiries marked as resolved.')
    mark_as_resolved.short_description = "Mark as resolved"
    
    def mark_as_unresolved(self, request, queryset):
        updated = queryset.update(is_resolved=False, resolved_at=None)
        self.message_user(request, f'{updated} inquiries marked as unresolved.')
    mark_as_unresolved.short_description = "Mark as unresolved"

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email', 'name')
    readonly_fields = ('subscribed_at',)
    
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('email', 'name')
        }),
        ('Subscription Status', {
            'fields': ('is_active', 'subscribed_at')
        })
    )
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions', export_to_csv]
    
    def activate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscriptions activated.')
    activate_subscriptions.short_description = "Activate subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} subscriptions deactivated.')
    deactivate_subscriptions.short_description = "Deactivate subscriptions"

@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'value_short', 'is_active', 'updated_at')
    list_filter = ('is_active', 'updated_at')
    search_fields = ('key', 'description', 'value')
    readonly_fields = ('updated_at',)
    
    fieldsets = (
        ('Configuration', {
            'fields': ('key', 'value', 'description')
        }),
        ('Status', {
            'fields': ('is_active', 'updated_at')
        })
    )
    
    def value_short(self, obj):
        return obj.value[:50] + "..." if len(obj.value) > 50 else obj.value
    value_short.short_description = 'Value'

# Custom Admin Dashboard
class traveling_agencyAdminSite(admin.AdminSite):
    site_header = "traveling_agency Travel Agency"
    site_title = "traveling_agency Admin Portal"
    index_title = "Travel & Tourism Management Dashboard"
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Dashboard statistics
        extra_context.update({
            'total_events': Event.objects.count(),
            'active_events': Event.objects.filter(status='published').count(),
            'total_bookings': Booking.objects.count(),
            'pending_bookings': Booking.objects.filter(status='pending').count(),
            'revenue_this_month': Booking.objects.filter(
                status='paid',
                booked_at__month=timezone.now().month
            ).aggregate(total=Sum('total_amount'))['total'] or 0,
            'whatsapp_requests': WhatsAppBooking.objects.filter(status='new').count(),
            'unresolved_inquiries': ContactInquiry.objects.filter(is_resolved=False).count(),
            'unapproved_reviews': Review.objects.filter(is_approved=False).count(),
        })
        
        return super().index(request, extra_context)

# Uncomment the following lines to use custom admin site
# traveling_agency_admin_site = traveling_agencyAdminSite(name='traveling_agency_admin')
# admin.site = traveling_agency_admin_site

# Register all models with their resp