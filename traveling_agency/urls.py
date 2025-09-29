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

    # admin views
    # Dashboard
    # Authentication URLs
    path('login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.admin_logout_view, name='admin_logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),

    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Events Management
    path('admin-events/', views.admin_events_list, name='admin_events_list'),
    path('admin-events/create/', views.admin_event_create, name='admin_event_create'),
    path('admin-events/<int:event_id>/', views.admin_event_detail, name='admin_event_detail'),
    path('admin-events/<int:event_id>/edit/', views.admin_event_edit, name='admin_event_edit'),
    path('admin-events/<int:event_id>/delete/', views.admin_event_delete, name='admin_event_delete'),
    path('admin-events/<int:event_id>/bookings/', views.admin_event_bookings, name='admin_event_bookings'),
    
    # PDF exports
    path('admin-events/<int:event_id>/export-bookings/', views.export_event_bookings_pdf, name='export_event_bookings_pdf'),
    path('admin-bookings/<uuid:booking_id>/export-voucher/', views.export_single_booking_pdf, name='export_single_booking_pdf'),
    
    # Image management (optional - for deleting images)
    path('admin-events/images/<int:image_id>/delete/', views.delete_event_image, name='delete_event_image'),
    
    # Bookings Management
    path('admin-bookings/', views.admin_bookings_list, name='admin_bookings_list'),
    path('admin-bookings/<uuid:booking_id>/', views.admin_booking_detail, name='admin_booking_detail'),
    path('admin-bookings/<uuid:booking_id>/update-status/', views.admin_booking_update_status, name='admin_booking_update_status'),
    
    # Payments Management
    path('admin-payments/', views.admin_payments_list, name='admin_payments_list'),
    
    # WhatsApp Bookings
    path('admin-whatsapp/', views.admin_whatsapp_bookings, name='admin_whatsapp_bookings'),
    path('admin-whatsapp/<int:booking_id>/process/', views.admin_whatsapp_process, name='admin_whatsapp_process'),
    
    # Reviews Management
    path('admin-reviews/', views.admin_reviews_list, name='admin_reviews_list'),
    path('admin-reviews/<int:review_id>/approve/', views.admin_review_approve, name='admin_review_approve'),
    
    # Categories Management
    path('admin-categories/', views.admin_categories_list, name='admin_categories_list'),
    path('admin-categories/create/', views.admin_category_create, name='admin_category_create'),
    path('admin-categories/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
    
    # Locations Management
    path('admin-locations/', views.admin_locations_list, name='admin_locations_list'),
    path('admin-locations/create/', views.admin_location_create, name='admin_location_create'),
    
    # Contact Inquiries
    path('admin-inquiries/', views.admin_inquiries_list, name='admin_inquiries_list'),
    path('inquiries/<int:inquiry_id>/', views.admin_inquiry_detail, name='admin_inquiry_detail'),
    
    # Newsletter Subscribers
    path('admin-newsletter/', views.admin_newsletter_subscribers, name='admin_newsletter_subscribers'),
    
    # Settings
    path('admin-settings/', views.admin_settings, name='admin_settings'),
    
    # Analytics
    path('admin-analytics/', views.admin_analytics, name='admin_analytics'),
    
    # Export Functions
    path('admin-export/bookings/', views.export_bookings, name='admin_export_bookings'),
    path('admin-export/payments/', views.export_payments, name='admin_export_payments'),
]
