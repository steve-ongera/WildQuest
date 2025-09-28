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

