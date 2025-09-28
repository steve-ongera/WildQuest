from django.db.models import Count, Q
from django.utils import timezone
from django.core.cache import cache
from .models import (
    Category, 
    Event, 
    Location, 
    SystemConfiguration,
    EventFeature
)

def site_wide_context(request):
    """
    Context processor to provide site-wide data for all templates
    """
    # Cache key for performance
    cache_key = 'site_wide_context_data'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data
    
    # Get active categories with event counts
    categories = Category.objects.filter(
        is_active=True
    ).annotate(
        event_count=Count('event', filter=Q(
            event__status='published',
            event__start_date__gte=timezone.now()
        ))
    ).order_by('name')
    
    # Get popular locations
    popular_locations = Location.objects.filter(
        is_popular=True
    ).order_by('name')[:8]
    
    # Get featured/upcoming events for quick access
    featured_events = Event.objects.filter(
        status='published',
        featured=True,
        start_date__gte=timezone.now()
    ).select_related('location', 'category')[:6]
    
    # Get system configurations
    system_configs = {}
    configs = SystemConfiguration.objects.filter(is_active=True)
    for config in configs:
        system_configs[config.key] = config.value
    
    # Get event types for filtering
    event_types = Event.EVENT_TYPES
    
    # Get popular event features
    popular_features = EventFeature.objects.all()[:10]
    
    # Company contact info (you can also store these in SystemConfiguration)
    contact_info = {
        'phone': system_configs.get('company_phone', '+254 712 345 678'),
        'email': system_configs.get('company_email', 'info@wildquest.co.ke'),
        'address': system_configs.get('company_address', 'Nairobi, Kenya'),
        'whatsapp': system_configs.get('whatsapp_number', '+254 712 345 678'),
    }
    
    # Social media links
    social_links = {
        'facebook': system_configs.get('facebook_url', '#'),
        'twitter': system_configs.get('twitter_url', '#'),
        'instagram': system_configs.get('instagram_url', '#'),
        'youtube': system_configs.get('youtube_url', '#'),
        'linkedin': system_configs.get('linkedin_url', '#'),
    }
    
    # Site statistics for homepage/about
    site_stats = {
        'total_events': Event.objects.filter(status='published').count(),
        'active_categories': categories.filter(event_count__gt=0).count(),
        'total_locations': Location.objects.count(),
        'upcoming_events': Event.objects.filter(
            status='published',
            start_date__gte=timezone.now()
        ).count(),
    }
    
    # Current year for copyright
    current_year = timezone.now().year
    
    context_data = {
        # Navigation data
        'nav_categories': categories,
        'popular_locations': popular_locations,
        'event_types': event_types,
        
        # Featured content
        'featured_events': featured_events,
        'popular_features': popular_features,
        
        # Company information
        'contact_info': contact_info,
        'social_links': social_links,
        
        # Site data
        'site_stats': site_stats,
        'current_year': current_year,
        
        # System configurations
        'system_configs': system_configs,
        
        # Utility data
        'now': timezone.now(),
    }
    
    # Cache for 15 minutes
    cache.set(cache_key, context_data, 60 * 15)
    
    return context_data


def booking_context(request):
    """
    Context processor for booking-related data
    """
    cache_key = f'booking_context_{request.user.id if request.user.is_authenticated else "anonymous"}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data
    
    context_data = {}
    
    # If user is authenticated, get their booking history
    if request.user.is_authenticated:
        from .models import Booking
        
        user_bookings = Booking.objects.filter(
            user=request.user
        ).select_related('event').order_by('-booked_at')[:5]
        
        context_data.update({
            'user_recent_bookings': user_bookings,
            'user_booking_count': user_bookings.count(),
        })
    
    # Get booking-related system configs
    booking_configs = {
        'whatsapp_booking_enabled': True,  # from system config
        'online_payment_enabled': True,   # from system config
        'booking_terms_url': '#',         # from system config
    }
    
    context_data.update({
        'booking_configs': booking_configs,
    })
    
    # Cache for 10 minutes
    cache.set(cache_key, context_data, 60 * 10)
    
    return context_data


def seo_context(request):
    """
    Context processor for SEO-related data
    """
    # Default SEO data that can be overridden in templates
    seo_data = {
        'default_title': 'WildQuest Kenya - Explore Tours, Safaris & Travel Adventures',
        'default_description': 'WildQuest is Kenya\'s trusted travel agency offering affordable safaris, tours, beach holidays, and adventure travel packages across Kenya.',
        'default_keywords': 'WildQuest, Kenya travel agency, Kenya safaris, Maasai Mara tours, Diani beach holidays, Nairobi city tours, adventure travel Kenya, cultural tours Kenya, travel packages Kenya',
        'site_name': 'WildQuest Kenya',
        'default_image': '/static/img/og-image.jpg',  # You'll need to add this
    }
    
    return {
        'seo_data': seo_data,
    }


def newsletter_context(request):
    """
    Context processor for newsletter functionality
    """
    # Newsletter form data
    newsletter_data = {
        'newsletter_enabled': True,
        'newsletter_placeholder': 'Enter Your Email',
        'newsletter_success_message': 'Thank you for subscribing to our newsletter!',
        'newsletter_error_message': 'Please enter a valid email address.',
    }
    
    return {
        'newsletter_data': newsletter_data,
    }