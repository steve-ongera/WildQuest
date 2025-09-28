from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import json
import uuid

from .models import (
    Event, Category, Location, Booking, BookingParticipant, 
    Payment, WhatsAppBooking, Review, FAQ, Itinerary, 
    EventImage, PricingTier, ContactInquiry, NewsletterSubscription,
    EventFeature, EventFeatureAssignment
)
from .forms import BookingForm, ContactForm, ReviewForm, NewsletterForm

def index(request):
    """Homepage view"""
    # First get featured events
    featured_events = list(
        Event.objects.filter(
            status='published',
            featured=True,
            start_date__gte=timezone.now()
        )
        .select_related('category', 'location')
        .prefetch_related('images')[:6]
    )

    # If fewer than 6, add extra published events to fill
    if len(featured_events) < 6:
        extra_needed = 6 - len(featured_events)
        extra_events = Event.objects.filter(
            status='published',
            start_date__gte=timezone.now()
        ).exclude(id__in=[e.id for e in featured_events]) \
         .select_related('category', 'location') \
         .prefetch_related('images')[:extra_needed]
        featured_events.extend(extra_events)

    popular_categories = Category.objects.filter(is_active=True).annotate(
        event_count=Count('event')
    ).order_by('-event_count')[:6]

    recent_reviews = Review.objects.filter(
        is_approved=True
    ).select_related('event').order_by('-created_at')[:6]

    context = {
        'featured_events': featured_events,
        'popular_categories': popular_categories,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'wildquest/index.html', context)


def about(request):
    """About page view"""
    return render(request, 'wildquest/about.html')

def services(request):
    """Services page view"""
    categories = Category.objects.filter(is_active=True).annotate(
        event_count=Count('event')
    )
    return render(request, 'wildquest/services.html', {'categories': categories})

def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'wildquest/contact.html', {'form': form})

def events_list(request):
    """List all events with filtering and pagination"""
    events = Event.objects.filter(
        status='published',
        start_date__gte=timezone.now()
    ).select_related('category', 'location').prefetch_related('images')
    
    # Filtering
    category_slug = request.GET.get('category')
    event_type = request.GET.get('type')
    location_id = request.GET.get('location')
    search = request.GET.get('search')
    sort = request.GET.get('sort', 'date')
    
    if category_slug:
        events = events.filter(category__slug=category_slug)
    
    if event_type:
        events = events.filter(event_type=event_type)
    
    if location_id:
        events = events.filter(location_id=location_id)
    
    if search:
        events = events.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(location__name__icontains=search)
        )
    
    # Sorting
    if sort == 'price':
        events = events.order_by('base_price')
    elif sort == 'price_desc':
        events = events.order_by('-base_price')
    elif sort == 'popularity':
        events = events.annotate(booking_count=Count('booking')).order_by('-booking_count')
    else:
        events = events.order_by('start_date')
    
    # Pagination
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Filter options for sidebar
    categories = Category.objects.filter(is_active=True)
    locations = Location.objects.filter(event__status='published').distinct()
    event_types = Event.EVENT_TYPES
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'locations': locations,
        'event_types': event_types,
        'current_filters': {
            'category': category_slug,
            'type': event_type,
            'location': location_id,
            'search': search,
            'sort': sort,
        }
    }
    return render(request, 'events/list.html', context)

def event_detail(request, slug):
    """Event detail view"""
    event = get_object_or_404(
        Event.objects.select_related('category', 'location')
        .prefetch_related('images', 'pricing_tiers', 'itinerary', 'faqs'),
        slug=slug,
        status='published'
    )
    
    # Reviews with ratings
    reviews = event.reviews.filter(is_approved=True).order_by('-created_at')
    avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
    
    # Related events
    related_events = Event.objects.filter(
        category=event.category,
        status='published',
        start_date__gte=timezone.now()
    ).exclude(id=event.id)[:4]
    
    # Features
    features = EventFeatureAssignment.objects.filter(
        event=event
    ).select_related('feature')
    
    context = {
        'event': event,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'related_events': related_events,
        'features': features,
        'is_booking_open': event.is_booking_open,
    }
    return render(request, 'events/detail.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Event, Booking, BookingParticipant
from .forms import BookingForm
import logging

# Set up logging for debugging
logger = logging.getLogger(__name__)

def booking_create(request, event_slug):
    """Create a new booking with enhanced error handling"""
    event = get_object_or_404(Event, slug=event_slug, status='published')
    
    if not event.is_booking_open:
        messages.error(request, 'Booking is not available for this event.')
        return redirect('event_detail', slug=event_slug)
    
    if request.method == 'POST':
        # Debug: Print POST data
        logger.debug(f"POST data: {request.POST}")
        
        form = BookingForm(request.POST, event=event)
        
        # Debug: Check form validity and errors
        if not form.is_valid():
            logger.error(f"Form errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
            context = {
                'event': event,
                'form': form,
                'pricing_tiers': event.pricing_tiers.filter(is_active=True),
            }
            return render(request, 'bookings/create.html', context)
        
        try:
            with transaction.atomic():
                # Create booking
                booking = form.save(commit=False)
                booking.event = event
                booking.user = request.user if request.user.is_authenticated else None
                
                # Calculate pricing
                pricing_tier = form.cleaned_data.get('pricing_tier')
                adults = form.cleaned_data['adults_count']
                children = form.cleaned_data['children_count']
                
                logger.debug(f"Adults: {adults}, Children: {children}, Pricing tier: {pricing_tier}")
                
                if pricing_tier:
                    base_amount = pricing_tier.price * adults
                    if event.child_price and children > 0:
                        base_amount += event.child_price * children
                else:
                    base_amount = event.base_price * adults
                    if event.child_price and children > 0:
                        base_amount += event.child_price * children
                
                # Apply group discount if applicable
                total_participants = adults + children
                discount_amount = 0
                if total_participants >= 5 and event.group_discount_percentage > 0:
                    discount_amount = base_amount * (event.group_discount_percentage / 100)
                
                booking.base_amount = base_amount
                booking.discount_amount = discount_amount
                booking.total_amount = base_amount - discount_amount
                booking.number_of_participants = total_participants
                
                logger.debug(f"Booking amounts - Base: {base_amount}, Discount: {discount_amount}, Total: {booking.total_amount}")
                
                # Save booking first
                booking.save()
                logger.debug(f"Booking saved with ID: {booking.booking_id}")
                
                # Create participants
                participant_names = request.POST.getlist('participant_names[]')
                participant_ages = request.POST.getlist('participant_ages[]')
                participant_types = request.POST.getlist('participant_types[]')
                participant_ids = request.POST.getlist('participant_ids[]')
                
                logger.debug(f"Participant data - Names: {participant_names}, Ages: {participant_ages}, Types: {participant_types}")
                
                participants_created = 0
                for i, name in enumerate(participant_names):
                    if name and name.strip():
                        age = None
                        if i < len(participant_ages) and participant_ages[i]:
                            try:
                                age = int(participant_ages[i])
                            except (ValueError, IndexError):
                                age = None
                        
                        participant_type = participant_types[i] if i < len(participant_types) else 'adult'
                        id_number = participant_ids[i] if i < len(participant_ids) else ''
                        
                        BookingParticipant.objects.create(
                            booking=booking,
                            name=name.strip(),
                            age=age,
                            participant_type=participant_type,
                            id_number=id_number.strip() if id_number else ''
                        )
                        participants_created += 1
                
                logger.debug(f"Created {participants_created} participants")
                
                # Update event booking count
                event.current_bookings += total_participants
                event.save()
                
                logger.debug(f"Updated event booking count to: {event.current_bookings}")
                
                messages.success(
                    request, 
                    f'Booking created successfully! Your booking ID is {booking.booking_id}. '
                    f'We will contact you via {booking.get_booking_method_display().lower()} shortly.'
                )
                return redirect('booking_detail', booking_id=booking.booking_id)
                
        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}")
            messages.error(request, f'Error creating booking: {str(e)}. Please try again.')
    
    else:
        form = BookingForm(event=event)
    
    context = {
        'event': event,
        'form': form,
        'pricing_tiers': event.pricing_tiers.filter(is_active=True),
    }
    return render(request, 'bookings/create.html', context)



@require_http_methods(["GET"])
def booking_detail(request, booking_id):
    """View booking details"""
    booking = get_object_or_404(
        Booking.objects.select_related('event', 'pricing_tier')
        .prefetch_related('participants', 'payments'),
        booking_id=booking_id
    )
    
    # Check if user has access to this booking
    if request.user.is_authenticated and booking.user != request.user:
        if not request.user.is_staff:
            raise Http404
    
    context = {
        'booking': booking,
    }
    return render(request, 'bookings/detail.html', context)


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template.loader import get_template
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from xhtml2pdf import pisa
from io import BytesIO
import qrcode
import base64
from PIL import Image
import os
from .models import Booking

def generate_booking_receipt_pdf(request, booking_id):
    """Generate and download compact PDF receipt for booking"""
    booking = get_object_or_404(
        Booking.objects.select_related('event', 'pricing_tier', 'event__location', 'event__category')
        .prefetch_related('participants', 'payments'),
        booking_id=booking_id
    )
    
    # Check if user has access to this booking
    if request.user.is_authenticated and booking.user != request.user:
        if not request.user.is_staff:
            raise Http404("You don't have permission to access this receipt.")
    
    # Generate compact QR Code for booking verification
    qr_data = f"WQ-{booking.booking_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,  # Smaller box size for compact receipt
        border=2,    # Smaller border
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64 for embedding in HTML
    buffered = BytesIO()
    qr_img.save(buffered, format="PNG")
    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    # Prepare context for template
    context = {
        'booking': booking,
        'event': booking.event,
        'participants': booking.participants.all(),
        'payments': booking.payments.all(),
        'qr_code': qr_code_base64,
        'receipt_date': timezone.now(),
        'company_info': {
            'name': 'WildQuest Kenya',
            'address': 'Nairobi, Kenya',
            'phone': '+254 712 345 678',
            'email': 'info@wildquest.co.ke',
            'website': 'www.wildquest.co.ke',
            'registration': 'CR/2024/001234',
        }
    }
    
    # Render HTML template
    template = get_template('bookings/receipt_pdf.html')  # Updated template name
    html = template.render(context)
    
    # Create PDF with compact settings
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="WildQuest_Receipt_{booking.booking_id}.pdf"'
    
    # Generate PDF with optimized settings for small receipt
    pisa_status = pisa.CreatePDF(
        html, 
        dest=response,
        encoding='utf-8',
        show_error_as_pdf=True
    )
    
    if pisa_status.err:
        return HttpResponse('Error generating receipt. Please try again or contact support.')
    
    return response


def booking_receipt_preview(request, booking_id):
    """Preview the compact receipt before downloading"""
    booking = get_object_or_404(
        Booking.objects.select_related('event', 'pricing_tier', 'event__location', 'event__category')
        .prefetch_related('participants', 'payments'),
        booking_id=booking_id
    )
    
    # Check permissions
    if request.user.is_authenticated and booking.user != request.user:
        if not request.user.is_staff:
            raise Http404("You don't have permission to access this receipt.")
    
    # Generate QR Code
    qr_data = f"WQ-{booking.booking_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,  # Slightly larger for preview
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    qr_img.save(buffered, format="PNG")
    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    context = {
        'booking': booking,
        'event': booking.event,
        'participants': booking.participants.all(),
        'payments': booking.payments.all(),
        'qr_code': qr_code_base64,
        'receipt_date': timezone.now(),
        'company_info': {
            'name': 'WildQuest Kenya',
            'address': 'Nairobi, Kenya',
            'phone': '+254 712 345 678',
            'email': 'info@wildquest.co.ke',
            'website': 'www.wildquest.co.ke',
            'registration': 'CR/2024/001234',
        }
    }
    
    return render(request, 'bookings/receipt_preview.html', context)


# Utility function to verify QR codes (for admin use)
def admin_approve_receipt(request, qr_data):
    """Verify booking from QR code scan"""
    if not request.user.is_staff:
        raise Http404("Permission denied")
    
    try:
        # Extract booking ID from QR data
        if qr_data.startswith('WQ-'):
            booking_id = qr_data[3:]  # Remove 'WQ-' prefix
            booking = get_object_or_404(Booking, booking_id=booking_id)
            
            context = {
                'booking': booking,
                'verification_time': timezone.now(),
                'verified_by': request.user,
            }
            return render(request, 'admin/booking_verification.html', context)
        else:
            messages.error(request, 'Invalid QR code format.')
            return redirect('index')
            
    except Exception as e:
        messages.error(request, f'Error verifying booking: {str(e)}')
        return redirect('index')

def whatsapp_booking(request, event_slug):
    """Handle WhatsApp booking requests"""
    event = get_object_or_404(Event, slug=event_slug, status='published')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        participants = request.POST.get('participants', 1)
        message = request.POST.get('message', '')
        
        # Create WhatsApp booking record
        whatsapp_booking = WhatsAppBooking.objects.create(
            event=event,
            customer_name=name,
            customer_phone=phone,
            message=message,
            participants_count=int(participants)
        )
        
        # Generate WhatsApp message
        whatsapp_message = f"""Hi WildQuest Kenya!

I'm interested in booking: {event.title}
Name: {name}
Phone: {phone}
Participants: {participants}
Message: {message}

Event Details:
- Date: {event.start_date.strftime('%B %d, %Y')}
- Duration: {event.duration_days} days
- Price: KES {event.base_price:,}

Please confirm availability and next steps.

Booking Reference: {whatsapp_booking.id}"""
        
        whatsapp_url = f"https://wa.me/254712345678?text={whatsapp_message.replace(' ', '%20').replace('\n', '%0A')}"
        
        return JsonResponse({
            'success': True,
            'whatsapp_url': whatsapp_url,
            'booking_ref': whatsapp_booking.id
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def category_events(request, slug):
    """Events by category"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    events = Event.objects.filter(
        category=category,
        status='published',
        start_date__gte=timezone.now()
    ).select_related('location').prefetch_related('images')
    
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'events/category.html', context)

def search_events(request):
    """Search events"""
    query = request.GET.get('q', '')
    events = Event.objects.none()
    
    if query:
        events = Event.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(location__name__icontains=query),
            status='published',
            start_date__gte=timezone.now()
        ).select_related('category', 'location').prefetch_related('images')
    
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'page_obj': page_obj,
    }
    return render(request, 'events/search.html', context)

def add_review(request, event_slug):
    """Add review for an event"""
    event = get_object_or_404(Event, slug=event_slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.event = event
            
            # Check if user has a booking for this event
            if request.user.is_authenticated:
                booking = Booking.objects.filter(
                    event=event,
                    user=request.user,
                    status__in=['paid', 'completed']
                ).first()
                if booking:
                    review.booking = booking
                    review.is_verified = True
            
            review.save()
            messages.success(request, 'Thank you for your review! It will be published after approval.')
            return redirect('event_detail', slug=event_slug)
    else:
        form = ReviewForm()
    
    context = {
        'event': event,
        'form': form,
    }
    return render(request, 'reviews/add.html', context)

@require_POST
def subscribe_newsletter(request):
    """Subscribe to newsletter"""
    email = request.POST.get('email')
    name = request.POST.get('name', '')
    
    if email:
        subscription, created = NewsletterSubscription.objects.get_or_create(
            email=email,
            defaults={'name': name}
        )
        
        if created:
            return JsonResponse({'success': True, 'message': 'Successfully subscribed!'})
        else:
            return JsonResponse({'success': False, 'message': 'Email already subscribed.'})
    
    return JsonResponse({'success': False, 'message': 'Please provide a valid email.'})

def booking_confirmation(request, booking_id):
    """Booking confirmation page"""
    booking = get_object_or_404(Booking, booking_id=booking_id)
    
    context = {
        'booking': booking,
    }
    return render(request, 'bookings/confirmation.html', context)

def event_calendar(request):
    """Calendar view of events"""
    events = Event.objects.filter(
        status='published',
        start_date__gte=timezone.now()
    ).select_related('category', 'location')
    
    # Format events for calendar
    calendar_events = []
    for event in events:
        calendar_events.append({
            'title': event.title,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat(),
            'url': reverse('event_detail', args=[event.slug]),
            'backgroundColor': '#007bff',
            'borderColor': '#007bff',
        })
    
    context = {
        'calendar_events': json.dumps(calendar_events),
    }
    return render(request, 'events/calendar.html', context)

def locations_list(request):
    """List all locations"""
    locations = Location.objects.filter(
        event__status='published'
    ).annotate(
        event_count=Count('event')
    ).distinct().order_by('name')
    
    context = {
        'locations': locations,
    }
    return render(request, 'locations/list.html', context)

def location_detail(request, location_id):
    """Location detail with events"""
    location = get_object_or_404(Location, id=location_id)
    events = Event.objects.filter(
        location=location,
        status='published',
        start_date__gte=timezone.now()
    ).select_related('category').prefetch_related('images')
    
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'location': location,
        'page_obj': page_obj,
    }
    return render(request, 'wildquest/locations/detail.html', context)

# API Views for AJAX requests
def get_event_pricing(request, event_id):
    """Get pricing information for an event"""
    event = get_object_or_404(Event, id=event_id)
    
    pricing_data = {
        'base_price': float(event.base_price),
        'child_price': float(event.child_price) if event.child_price else None,
        'group_discount': float(event.group_discount_percentage),
        'pricing_tiers': []
    }
    
    for tier in event.pricing_tiers.filter(is_active=True):
        pricing_data['pricing_tiers'].append({
            'id': tier.id,
            'name': tier.name,
            'price': float(tier.price),
            'available_spots': tier.available_spots,
            'description': tier.description
        })
    
    return JsonResponse(pricing_data)

def check_availability(request, event_id):
    """Check event availability"""
    event = get_object_or_404(Event, id=event_id)
    participants = int(request.GET.get('participants', 1))
    
    available = event.available_spots >= participants and event.is_booking_open
    
    return JsonResponse({
        'available': available,
        'available_spots': event.available_spots,
        'is_booking_open': event.is_booking_open,
        'message': 'Available' if available else 'Not enough spots available'
    })



def feature(request):
    return render(request, 'feature.html')

def project(request):
    return render(request, 'project.html')

def team(request):
    return render(request, 'team.html')

def testimonial(request):
    return render(request, 'testimonial.html')

# Custom 404 page
def custom_404(request, exception):
    return render(request, '404.html', status=404)
def custom_500(request):
    return render(request, '500.html', status=500)
def custom_403(request, exception):
    return render(request, '403.html', status=403)
def custom_400(request, exception):
    return render(request, '400.html', status=400)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.template.response import TemplateResponse
import csv
import json
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    Event, Booking, Payment, Category, Location, EventImage, PricingTier,
    BookingParticipant, WhatsAppBooking, Review, FAQ, Itinerary,
    EventFeature, EventFeatureAssignment, ContactInquiry, SystemConfiguration,
    NewsletterSubscription
)
from .forms import (
    EventForm, CategoryForm, LocationForm, PricingTierForm, EventImageForm,
    SystemConfigurationForm, ContactInquiryResponseForm
)

# ===== VIEWS.PY =====
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.decorators import method_decorator
from django.views.generic import View
from django import forms


class LoginForm(forms.Form):
    """Custom login form"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


@sensitive_post_parameters('password')
@csrf_protect
@never_cache
def admin_login_view(request):
    """Custom admin login view"""
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            # Try to authenticate
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active and (user.is_staff or user.is_superuser):
                    login(request, user)
                    
                    # Set session expiry based on remember me
                    if not remember_me:
                        request.session.set_expiry(0)  # Browser session
                    else:
                        request.session.set_expiry(1209600)  # 2 weeks
                    
                    # Redirect to next URL or dashboard
                    next_url = request.GET.get('next', reverse('admin_dashboard'))
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect(next_url)
                else:
                    if not user.is_active:
                        messages.error(request, 'Your account has been deactivated.')
                    else:
                        messages.error(request, 'You do not have permission to access the admin area.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'title': 'Admin Login',
        'next': request.GET.get('next', ''),
    }
    return render(request, 'admin/auth/login.html', context)


@login_required
def admin_logout_view(request):
    """Custom admin logout view"""
    user_name = request.user.get_full_name() or request.user.username
    logout(request)
    messages.success(request, f'You have been logged out successfully. Goodbye, {user_name}!')
    return redirect('admin_login')


@method_decorator([login_required, never_cache], name='dispatch')
class ProfileView(View):
    """User profile view"""
    
    def get(self, request):
        context = {
            'user': request.user,
            'title': 'Profile',
        }
        return render(request, 'admin/auth/profile.html', context)





def admin_required(user):
    return user.is_staff or user.is_superuser


@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard with key metrics"""
    # Date ranges for analytics
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # Key metrics
    total_events = Event.objects.count()
    active_events = Event.objects.filter(status='published').count()
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    
    # Revenue metrics
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    revenue_30_days = Payment.objects.filter(
        status='completed',
        completed_at__gte=last_30_days
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Recent activity
    recent_bookings = Booking.objects.select_related('event').order_by('-booked_at')[:10]
    recent_payments = Payment.objects.select_related('booking__event').order_by('-initiated_at')[:10]
    pending_whatsapp = WhatsAppBooking.objects.filter(status='new').count()
    unresolved_inquiries = ContactInquiry.objects.filter(is_resolved=False).count()
    
    # Chart data for bookings over time
    booking_chart_data = []
    for i in range(30, 0, -1):
        date = today - timedelta(days=i)
        bookings_count = Booking.objects.filter(booked_at__date=date).count()
        booking_chart_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'bookings': bookings_count
        })
    
    # Popular events
    popular_events = Event.objects.annotate(
        booking_count=Count('booking')
    ).order_by('-booking_count')[:5]
    
    context = {
        'total_events': total_events,
        'active_events': active_events,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'total_revenue': total_revenue,
        'revenue_30_days': revenue_30_days,
        'recent_bookings': recent_bookings,
        'recent_payments': recent_payments,
        'pending_whatsapp': pending_whatsapp,
        'unresolved_inquiries': unresolved_inquiries,
        'booking_chart_data': json.dumps(booking_chart_data),
        'popular_events': popular_events,
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def admin_events_list(request):
    """List all events with filters"""
    events = Event.objects.select_related('category', 'location', 'created_by').all()
    
    # Filters
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    location_filter = request.GET.get('location')
    search = request.GET.get('search')
    
    if status_filter:
        events = events.filter(status=status_filter)
    
    if category_filter:
        events = events.filter(category_id=category_filter)
    
    if location_filter:
        events = events.filter(location_id=location_filter)
    
    if search:
        events = events.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(location__name__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(events, 20)
    page_number = request.GET.get('page')
    events_page = paginator.get_page(page_number)
    
    # Filter options
    categories = Category.objects.filter(is_active=True)
    locations = Location.objects.all()
    
    context = {
        'events': events_page,
        'categories': categories,
        'locations': locations,
        'status_choices': Event.STATUS_CHOICES,
        'filters': {
            'status': status_filter,
            'category': category_filter,
            'location': location_filter,
            'search': search,
        }
    }
    
    return render(request, 'admin/events/list.html', context)


@staff_member_required
def admin_event_detail(request, event_id):
    """Event detail view with bookings and analytics"""
    event = get_object_or_404(Event, id=event_id)
    
    # Event statistics
    bookings = event.booking_set.all()
    total_bookings = bookings.count()
    confirmed_bookings = bookings.filter(status__in=['confirmed', 'paid']).count()
    total_revenue = Payment.objects.filter(
        booking__event=event, 
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Recent bookings
    recent_bookings = bookings.select_related('pricing_tier').order_by('-booked_at')[:10]
    
    # Reviews
    reviews = event.reviews.filter(is_approved=True).order_by('-created_at')[:5]
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    
    context = {
        'event': event,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
    }
    
    return render(request, 'admin/events/detail.html', context)


@staff_member_required
def admin_event_create(request):
    """Create new event"""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, f'Event "{event.title}" created successfully.')
            return redirect('admin_event_detail', event_id=event.id)
    else:
        form = EventForm()
    
    return render(request, 'admin/events/create.html', {'form': form})


@staff_member_required
def admin_event_edit(request, event_id):
    """Edit existing event"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Event "{event.title}" updated successfully.')
            return redirect('admin_event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)
    
    return render(request, 'admin/events/edit.html', {'form': form, 'event': event})


@staff_member_required
@require_POST
def admin_event_delete(request, event_id):
    """Delete event"""
    event = get_object_or_404(Event, id=event_id)
    event_title = event.title
    event.delete()
    messages.success(request, f'Event "{event_title}" deleted successfully.')
    return redirect('admin_events_list')


@staff_member_required
def admin_bookings_list(request):
    """List all bookings with filters"""
    bookings = Booking.objects.select_related('event', 'pricing_tier').all()
    
    # Filters
    status_filter = request.GET.get('status')
    event_filter = request.GET.get('event')
    date_filter = request.GET.get('date')
    search = request.GET.get('search')
    
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    if event_filter:
        bookings = bookings.filter(event_id=event_filter)
    
    if date_filter:
        bookings = bookings.filter(booked_at__date=date_filter)
    
    if search:
        bookings = bookings.filter(
            Q(customer_name__icontains=search) |
            Q(customer_email__icontains=search) |
            Q(customer_phone__icontains=search) |
            Q(booking_id__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(bookings, 25)
    page_number = request.GET.get('page')
    bookings_page = paginator.get_page(page_number)
    
    # Filter options
    events = Event.objects.filter(status='published').order_by('title')
    
    context = {
        'bookings': bookings_page,
        'events': events,
        'status_choices': Booking.BOOKING_STATUS,
        'filters': {
            'status': status_filter,
            'event': event_filter,
            'date': date_filter,
            'search': search,
        }
    }
    
    return render(request, 'admin/bookings/list.html', context)


@staff_member_required
def admin_booking_detail(request, booking_id):
    """Booking detail view"""
    booking = get_object_or_404(
        Booking.objects.select_related('event', 'pricing_tier'),
        booking_id=booking_id
    )
    
    # Get participants
    participants = booking.participants.all()
    
    # Get payments
    payments = booking.payments.all().order_by('-initiated_at')
    
    context = {
        'booking': booking,
        'participants': participants,
        'payments': payments,
    }
    
    return render(request, 'admin/bookings/detail.html', context)


@staff_member_required
@require_POST
def admin_booking_update_status(request, booking_id):
    """Update booking status"""
    booking = get_object_or_404(Booking, booking_id=booking_id)
    new_status = request.POST.get('status')
    
    if new_status in dict(Booking.BOOKING_STATUS):
        old_status = booking.status
        booking.status = new_status
        
        if new_status == 'confirmed' and old_status != 'confirmed':
            booking.confirmed_at = timezone.now()
        
        booking.save()
        messages.success(request, f'Booking status updated to {new_status}.')
    else:
        messages.error(request, 'Invalid status.')
    
    return redirect('admin_booking_detail', booking_id=booking_id)


@staff_member_required
def admin_payments_list(request):
    """List all payments"""
    payments = Payment.objects.select_related('booking__event').all()
    
    # Filters
    status_filter = request.GET.get('status')
    method_filter = request.GET.get('method')
    date_filter = request.GET.get('date')
    
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    if method_filter:
        payments = payments.filter(payment_method=method_filter)
    
    if date_filter:
        payments = payments.filter(initiated_at__date=date_filter)
    
    # Pagination
    paginator = Paginator(payments, 25)
    page_number = request.GET.get('page')
    payments_page = paginator.get_page(page_number)
    
    # Summary stats
    total_completed = payments.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    total_pending = payments.filter(status='pending').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    context = {
        'payments': payments_page,
        'status_choices': Payment.PAYMENT_STATUS,
        'method_choices': Payment.PAYMENT_METHODS,
        'total_completed': total_completed,
        'total_pending': total_pending,
        'filters': {
            'status': status_filter,
            'method': method_filter,
            'date': date_filter,
        }
    }
    
    return render(request, 'admin/payments/list.html', context)


@staff_member_required
def admin_whatsapp_bookings(request):
    """Manage WhatsApp bookings"""
    bookings = WhatsAppBooking.objects.select_related('event', 'processed_by').all()
    
    # Filters
    status_filter = request.GET.get('status', 'new')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(bookings, 20)
    page_number = request.GET.get('page')
    bookings_page = paginator.get_page(page_number)
    
    context = {
        'bookings': bookings_page,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin/whatsapp/list.html', context)


@staff_member_required
@require_POST
def admin_whatsapp_process(request, booking_id):
    """Process WhatsApp booking"""
    whatsapp_booking = get_object_or_404(WhatsAppBooking, id=booking_id)
    action = request.POST.get('action')
    
    if action == 'approve':
        # Create actual booking from WhatsApp request
        booking = Booking.objects.create(
            event=whatsapp_booking.event,
            customer_name=whatsapp_booking.customer_name,
            customer_phone=whatsapp_booking.customer_phone,
            customer_email=f"{whatsapp_booking.customer_phone}@temp.com",  # Temporary email
            number_of_participants=whatsapp_booking.participants_count,
            adults_count=whatsapp_booking.participants_count,
            base_amount=whatsapp_booking.event.base_price * whatsapp_booking.participants_count,
            total_amount=whatsapp_booking.event.base_price * whatsapp_booking.participants_count,
            booking_method='whatsapp',
            status='confirmed'
        )
        
        whatsapp_booking.booking = booking
        whatsapp_booking.status = 'approved'
        whatsapp_booking.processed_by = request.user
        whatsapp_booking.processed_at = timezone.now()
        whatsapp_booking.save()
        
        messages.success(request, 'WhatsApp booking approved and converted to regular booking.')
    
    elif action == 'reject':
        whatsapp_booking.status = 'rejected'
        whatsapp_booking.processed_by = request.user
        whatsapp_booking.processed_at = timezone.now()
        whatsapp_booking.save()
        
        messages.success(request, 'WhatsApp booking rejected.')
    
    return redirect('admin_whatsapp_bookings')


@staff_member_required
def admin_reviews_list(request):
    """Manage reviews"""
    reviews = Review.objects.select_related('event', 'booking').all()
    
    # Filters
    status_filter = request.GET.get('status')
    if status_filter == 'approved':
        reviews = reviews.filter(is_approved=True)
    elif status_filter == 'pending':
        reviews = reviews.filter(is_approved=False)
    
    # Pagination
    paginator = Paginator(reviews, 20)
    page_number = request.GET.get('page')
    reviews_page = paginator.get_page(page_number)
    
    context = {
        'reviews': reviews_page,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin/reviews/list.html', context)


@staff_member_required
@require_POST
def admin_review_approve(request, review_id):
    """Approve or reject review"""
    review = get_object_or_404(Review, id=review_id)
    action = request.POST.get('action')
    
    if action == 'approve':
        review.is_approved = True
        messages.success(request, 'Review approved.')
    elif action == 'reject':
        review.is_approved = False
        messages.success(request, 'Review rejected.')
    
    review.save()
    return redirect('admin_reviews_list')


@staff_member_required
def admin_categories_list(request):
    """Manage categories"""
    categories = Category.objects.all().order_by('name')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'admin/categories/list.html', context)


@staff_member_required
def admin_category_create(request):
    """Create category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('admin_categories_list')
    else:
        form = CategoryForm()
    
    return render(request, 'admin/categories/create.html', {'form': form})


@staff_member_required
def admin_category_edit(request, category_id):
    """Edit category"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('admin_categories_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'admin/categories/edit.html', {'form': form, 'category': category})


@staff_member_required
def admin_locations_list(request):
    """Manage locations"""
    locations = Location.objects.all().order_by('name')
    
    context = {
        'locations': locations,
    }
    
    return render(request, 'admin/locations/list.html', context)


@staff_member_required
def admin_location_create(request):
    """Create location"""
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Location created successfully.')
            return redirect('admin_locations_list')
    else:
        form = LocationForm()
    
    return render(request, 'admin/locations/create.html', {'form': form})


@staff_member_required
def admin_inquiries_list(request):
    """Manage contact inquiries"""
    inquiries = ContactInquiry.objects.select_related('event', 'resolved_by').all()
    
    # Filters
    status_filter = request.GET.get('status')
    if status_filter == 'resolved':
        inquiries = inquiries.filter(is_resolved=True)
    elif status_filter == 'unresolved':
        inquiries = inquiries.filter(is_resolved=False)
    
    # Pagination
    paginator = Paginator(inquiries, 20)
    page_number = request.GET.get('page')
    inquiries_page = paginator.get_page(page_number)
    
    context = {
        'inquiries': inquiries_page,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin/inquiries/list.html', context)


@staff_member_required
def admin_inquiry_detail(request, inquiry_id):
    """View and respond to inquiry"""
    inquiry = get_object_or_404(ContactInquiry, id=inquiry_id)
    
    if request.method == 'POST':
        form = ContactInquiryResponseForm(request.POST)
        if form.is_valid():
            inquiry.admin_notes = form.cleaned_data['admin_notes']
            inquiry.is_resolved = form.cleaned_data['is_resolved']
            if inquiry.is_resolved and not inquiry.resolved_at:
                inquiry.resolved_at = timezone.now()
                inquiry.resolved_by = request.user
            inquiry.save()
            
            messages.success(request, 'Inquiry updated successfully.')
            return redirect('admin_inquiries_list')
    else:
        form = ContactInquiryResponseForm(initial={
            'admin_notes': inquiry.admin_notes,
            'is_resolved': inquiry.is_resolved,
        })
    
    return render(request, 'admin/inquiries/detail.html', {'inquiry': inquiry, 'form': form})


@staff_member_required
def admin_newsletter_subscribers(request):
    """Manage newsletter subscribers"""
    subscribers = NewsletterSubscription.objects.all().order_by('-subscribed_at')
    
    # Pagination
    paginator = Paginator(subscribers, 50)
    page_number = request.GET.get('page')
    subscribers_page = paginator.get_page(page_number)
    
    context = {
        'subscribers': subscribers_page,
        'total_subscribers': subscribers.filter(is_active=True).count(),
    }
    
    return render(request, 'admin/newsletter/list.html', context)


@staff_member_required
def admin_settings(request):
    """System settings"""
    settings = SystemConfiguration.objects.all().order_by('key')
    
    if request.method == 'POST':
        for setting in settings:
            new_value = request.POST.get(f'setting_{setting.id}')
            if new_value is not None:
                setting.value = new_value
                setting.save()
        
        messages.success(request, 'Settings updated successfully.')
        return redirect('admin_settings')
    
    context = {
        'settings': settings,
    }
    
    return render(request, 'admin/settings.html', context)


@staff_member_required
def admin_analytics(request):
    """Analytics dashboard"""
    # Date ranges
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_90_days = today - timedelta(days=90)
    
    # Revenue analytics
    daily_revenue = []
    for i in range(30, 0, -1):
        date = today - timedelta(days=i)
        revenue = Payment.objects.filter(
            status='completed',
            completed_at__date=date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        daily_revenue.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(revenue)
        })
    
    # Booking trends
    booking_trends = []
    for i in range(12, 0, -1):
        date = today - timedelta(days=i*30)
        bookings = Booking.objects.filter(
            booked_at__date__gte=date,
            booked_at__date__lt=date + timedelta(days=30)
        ).count()
        
        booking_trends.append({
            'month': date.strftime('%B'),
            'bookings': bookings
        })
    
    # Popular destinations
    popular_locations = Location.objects.annotate(
        event_count=Count('event'),
        booking_count=Count('event__booking')
    ).order_by('-booking_count')[:10]
    
    context = {
        'daily_revenue': json.dumps(daily_revenue),
        'booking_trends': json.dumps(booking_trends),
        'popular_locations': popular_locations,
    }
    
    return render(request, 'admin/analytics.html', context)


@staff_member_required
def export_bookings(request):
    """Export bookings to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bookings.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Booking ID', 'Event', 'Customer Name', 'Email', 'Phone',
        'Participants', 'Total Amount', 'Status', 'Booking Date'
    ])
    
    bookings = Booking.objects.select_related('event').all()
    for booking in bookings:
        writer.writerow([
            booking.booking_id,
            booking.event.title,
            booking.customer_name,
            booking.customer_email,
            booking.customer_phone,
            booking.number_of_participants,
            booking.total_amount,
            booking.get_status_display(),
            booking.booked_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response


@staff_member_required
def export_payments(request):
    """Export payments to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Payment ID', 'Booking ID', 'Event', 'Amount', 'Method',
        'Status', 'Transaction Ref', 'Date'
    ])
    
    payments = Payment.objects.select_related('booking__event').all()
    for payment in payments:
        writer.writerow([
            payment.payment_id,
            payment.booking.booking_id,
            payment.booking.event.title,
            payment.amount,
            payment.get_payment_method_display(),
            payment.get_status_display(),
            payment.transaction_reference,
            payment.initiated_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response

