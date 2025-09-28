from django.urls import path
from . import views

urlpatterns = [
     # Main pages
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='service'),
    path('contact/', views.contact, name='contact'),
    path('events/', views.events_list, name='events_list'),
    path('events/search/', views.search_events, name='search_events'),
    path('events/calendar/', views.event_calendar, name='event_calendar'),
    path('events/<slug:slug>/', views.event_detail, name='event_detail'),
    path('category/<slug:slug>/', views.category_events, name='category_events'),
    path('locations/', views.locations_list, name='locations_list'),
    path('locations/<int:location_id>/', views.location_detail, name='location_detail'),
    path('book/<slug:event_slug>/', views.booking_create, name='booking_create'),
    path('booking/<uuid:booking_id>/', views.booking_detail, name='booking_detail'),
    path('booking/<uuid:booking_id>/confirmation/', views.booking_confirmation, name='booking_confirmation'),
    path('whatsapp-book/<slug:event_slug>/', views.whatsapp_booking, name='whatsapp_booking'),
    path('review/<slug:event_slug>/', views.add_review, name='add_review'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('api/event/<int:event_id>/pricing/', views.get_event_pricing, name='get_event_pricing'),
    path('api/event/<int:event_id>/availability/', views.check_availability, name='check_availability'),

    # Booking receipt routes
    path('booking/<str:booking_id>/receipt/pdf/', views.generate_booking_receipt_pdf, name='booking_receipt_pdf'),
    path('booking/<str:booking_id>/receipt/preview/', views.booking_receipt_preview, name='booking_receipt_preview'),
    path('booking/<str:booking_id>/receipt/approve/', views.admin_approve_receipt, name='admin_approve_receipt'),

    # Additional informational pages
    path('feature/', views.feature, name='feature'),
    path('project/', views.project, name='project'),
    path('team/', views.team, name='team'),
    path('testimonial/', views.testimonial, name='testimonial'),
]
