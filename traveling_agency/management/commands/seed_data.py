import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid
from traveling_agency.models import (
    Category, Location, Event, EventImage, PricingTier, Booking, 
    BookingParticipant, Payment, WhatsAppBooking, Review, FAQ, 
    Itinerary, EventFeature, EventFeatureAssignment, NewsletterSubscription,
    ContactInquiry, SystemConfiguration
)

class Command(BaseCommand):
    help = 'Seed database with realistic Kenyan travel data for WildQuest platform'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting WildQuest database seeding...'))
        
        # Create superuser if doesn't exist
        self.create_admin_user()
        
        # Seed data in order (respecting foreign key dependencies)
        self.create_categories()
        self.create_locations()
        self.create_event_features()
        self.create_events()
        self.create_pricing_tiers()
        self.create_faqs()
        self.create_itineraries()
        self.create_bookings()
        self.create_payments()
        self.create_reviews()
        self.create_whatsapp_bookings()
        self.create_contact_inquiries()
        self.create_newsletter_subscriptions()
        self.create_system_configurations()
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))

    def create_admin_user(self):
        """Create admin user if doesn't exist"""
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='steve.ongera@wildquest.co.ke',
                password='wildquest2024',
                first_name='Steve',
                last_name='Ongera'
            )
        self.stdout.write('✓ Admin user created/verified')

    def create_categories(self):
        """Create travel experience categories"""
        categories_data = [
            {
                'name': 'Wildlife Safari',
                'slug': 'wildlife-safari',
                'description': 'Experience Kenya\'s incredible wildlife in their natural habitat',
                'icon': 'fas fa-binoculars'
            },
            {
                'name': 'Beach Holiday',
                'slug': 'beach-holiday',
                'description': 'Relax and unwind on Kenya\'s pristine coastal beaches',
                'icon': 'fas fa-umbrella-beach'
            },
            {
                'name': 'Mountain Climbing',
                'slug': 'mountain-climbing',
                'description': 'Conquer Kenya\'s majestic peaks and enjoy breathtaking views',
                'icon': 'fas fa-mountain'
            },
            {
                'name': 'Cultural Experience',
                'slug': 'cultural-experience',
                'description': 'Immerse yourself in Kenya\'s rich cultural heritage',
                'icon': 'fas fa-drum'
            },
            {
                'name': 'Adventure Sports',
                'slug': 'adventure-sports',
                'description': 'Thrilling outdoor activities and extreme sports',
                'icon': 'fas fa-parachute-box'
            },
            {
                'name': 'Road Trip',
                'slug': 'road-trip',
                'description': 'Scenic drives through Kenya\'s diverse landscapes',
                'icon': 'fas fa-car'
            },
            {
                'name': 'Corporate Retreat',
                'slug': 'corporate-retreat',
                'description': 'Team building and corporate events in unique settings',
                'icon': 'fas fa-building'
            }
        ]
        
        for cat_data in categories_data:
            Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
        self.stdout.write('✓ Categories created')

    def create_locations(self):
        """Create Kenyan locations and destinations"""
        locations_data = [
            # Coast Region
            {
                'name': 'Diani Beach',
                'county': 'Kwale',
                'region': 'Coast',
                'latitude': Decimal('-4.2947'),
                'longitude': Decimal('39.5808'),
                'description': 'One of Africa\'s leading beach destinations with pristine white sand beaches',
                'is_popular': True
            },
            {
                'name': 'Malindi',
                'county': 'Kilifi',
                'region': 'Coast',
                'latitude': Decimal('-3.2194'),
                'longitude': Decimal('40.1169'),
                'description': 'Historic coastal town with beautiful beaches and rich Swahili culture',
                'is_popular': True
            },
            {
                'name': 'Watamu',
                'county': 'Kilifi',
                'region': 'Coast',
                'latitude': Decimal('-3.3581'),
                'longitude': Decimal('40.0358'),
                'description': 'Marine national park with coral reefs and pristine beaches',
                'is_popular': True
            },
            {
                'name': 'Lamu Island',
                'county': 'Lamu',
                'region': 'Coast',
                'latitude': Decimal('-2.2717'),
                'longitude': Decimal('40.9020'),
                'description': 'UNESCO World Heritage site with ancient Swahili architecture',
                'is_popular': True
            },
            
            # Rift Valley Region
            {
                'name': 'Maasai Mara',
                'county': 'Narok',
                'region': 'Rift Valley',
                'latitude': Decimal('-1.4061'),
                'longitude': Decimal('35.0061'),
                'description': 'World-famous game reserve, home to the Great Migration',
                'is_popular': True
            },
            {
                'name': 'Lake Nakuru',
                'county': 'Nakuru',
                'region': 'Rift Valley',
                'latitude': Decimal('-0.3031'),
                'longitude': Decimal('36.0800'),
                'description': 'Soda lake famous for flamingos and rhino sanctuary',
                'is_popular': True
            },
            {
                'name': 'Hell\'s Gate National Park',
                'county': 'Nakuru',
                'region': 'Rift Valley',
                'latitude': Decimal('-0.9167'),
                'longitude': Decimal('36.3167'),
                'description': 'Dramatic landscape with geothermal features and rock climbing',
                'is_popular': False
            },
            {
                'name': 'Lake Naivasha',
                'county': 'Nakuru',
                'region': 'Rift Valley',
                'latitude': Decimal('-0.7167'),
                'longitude': Decimal('36.3333'),
                'description': 'Freshwater lake with hippos and diverse birdlife',
                'is_popular': True
            },
            
            # Central Region
            {
                'name': 'Mount Kenya',
                'county': 'Nyeri',
                'region': 'Central',
                'latitude': Decimal('-0.1500'),
                'longitude': Decimal('37.3083'),
                'description': 'Africa\'s second highest peak and UNESCO World Heritage site',
                'is_popular': True
            },
            {
                'name': 'Aberdare National Park',
                'county': 'Nyeri',
                'region': 'Central',
                'latitude': Decimal('-0.4167'),
                'longitude': Decimal('36.8333'),
                'description': 'Mountain range with dense forests and unique wildlife',
                'is_popular': False
            },
            {
                'name': 'Ol Pejeta Conservancy',
                'county': 'Laikipia',
                'region': 'Central',
                'latitude': Decimal('0.0000'),
                'longitude': Decimal('36.9000'),
                'description': 'Private conservancy with the last northern white rhinos',
                'is_popular': True
            },
            
            # Western Region
            {
                'name': 'Kakamega Forest',
                'county': 'Kakamega',
                'region': 'Western',
                'latitude': Decimal('0.2833'),
                'longitude': Decimal('34.8667'),
                'description': 'Last remnant of equatorial rainforest in Kenya',
                'is_popular': False
            },
            {
                'name': 'Lake Victoria',
                'county': 'Kisumu',
                'region': 'Western',
                'latitude': Decimal('-0.0917'),
                'longitude': Decimal('34.7680'),
                'description': 'Africa\'s largest lake with fishing communities',
                'is_popular': False
            },
            
            # Northern Region
            {
                'name': 'Samburu National Reserve',
                'county': 'Samburu',
                'region': 'Northern',
                'latitude': Decimal('0.5667'),
                'longitude': Decimal('37.5333'),
                'description': 'Semi-arid reserve with unique wildlife and Samburu culture',
                'is_popular': True
            },
            {
                'name': 'Turkana',
                'county': 'Turkana',
                'region': 'Northern',
                'latitude': Decimal('3.1167'),
                'longitude': Decimal('35.6000'),
                'description': 'Desert region with unique cultural experiences and Lake Turkana',
                'is_popular': False
            },
            
            # Eastern Region
            {
                'name': 'Tsavo National Park',
                'county': 'Taita Taveta',
                'region': 'Eastern',
                'latitude': Decimal('-2.3833'),
                'longitude': Decimal('38.4500'),
                'description': 'One of Kenya\'s largest national parks, famous for red elephants',
                'is_popular': True
            }
        ]
        
        for loc_data in locations_data:
            Location.objects.get_or_create(
                name=loc_data['name'],
                county=loc_data['county'],
                defaults=loc_data
            )
        self.stdout.write('✓ Locations created')

    def create_event_features(self):
        """Create event features and amenities"""
        features_data = [
            {'name': 'Professional Guide', 'icon': 'fas fa-user-tie', 'description': 'Experienced local guide included'},
            {'name': 'Transportation', 'icon': 'fas fa-bus', 'description': 'All transportation provided'},
            {'name': 'Accommodation', 'icon': 'fas fa-bed', 'description': 'Hotel/lodge accommodation included'},
            {'name': 'All Meals', 'icon': 'fas fa-utensils', 'description': 'Breakfast, lunch, and dinner included'},
            {'name': 'Game Drive', 'icon': 'fas fa-binoculars', 'description': 'Wildlife viewing drives'},
            {'name': 'Photography Support', 'icon': 'fas fa-camera', 'description': 'Professional photography assistance'},
            {'name': 'Cultural Activities', 'icon': 'fas fa-drum', 'description': 'Local cultural experiences'},
            {'name': 'Swimming Pool', 'icon': 'fas fa-swimming-pool', 'description': 'Pool access available'},
            {'name': 'Wi-Fi Internet', 'icon': 'fas fa-wifi', 'description': 'Internet connectivity provided'},
            {'name': 'Airport Transfer', 'icon': 'fas fa-plane-departure', 'description': 'Airport pickup and drop-off'},
            {'name': 'First Aid Kit', 'icon': 'fas fa-first-aid', 'description': 'Medical emergency kit available'},
            {'name': 'Snorkeling Gear', 'icon': 'fas fa-swimmer', 'description': 'Snorkeling equipment provided'},
            {'name': 'Hiking Equipment', 'icon': 'fas fa-mountain', 'description': 'Hiking gear available'},
            {'name': 'Life Jackets', 'icon': 'fas fa-life-ring', 'description': 'Safety equipment for water activities'},
            {'name': 'Camping Gear', 'icon': 'fas fa-campground', 'description': 'Camping equipment provided'}
        ]
        
        for feature_data in features_data:
            EventFeature.objects.get_or_create(
                name=feature_data['name'],
                defaults=feature_data
            )
        self.stdout.write('✓ Event features created')

    def create_events(self):
        """Create diverse travel events"""
        admin_user = User.objects.get(username='admin')
        
        events_data = [
            {
                'title': 'Maasai Mara Great Migration Safari',
                'slug': 'maasai-mara-great-migration-safari',
                'description': 'Experience the world\'s most spectacular wildlife phenomenon - the Great Migration. Witness millions of wildebeest, zebras, and gazelles crossing the Mara River in their eternal search for greener pastures. This 4-day safari includes game drives at prime locations, luxury tented accommodation, and expert guides who will help you capture the perfect shots of this natural wonder.',
                'short_description': 'Witness the Great Migration in Maasai Mara with luxury accommodation and expert guides',
                'event_type': 'safari',
                'category_slug': 'wildlife-safari',
                'location_name': 'Maasai Mara',
                'start_date': timezone.now() + timedelta(days=30),
                'duration_days': 4,
                'max_participants': 24,
                'min_participants': 2,
                'base_price': Decimal('45000'),
                'child_price': Decimal('35000'),
                'vip_price': Decimal('65000'),
                'group_discount_percentage': Decimal('10'),
                'includes': 'Transportation in 4WD safari vehicle, Professional guide, Park entry fees, Luxury tented accommodation, All meals, Game drives, Cultural visit to Maasai village, Airport transfers',
                'excludes': 'International flights, Visa fees, Travel insurance, Personal expenses, Alcoholic beverages, Tips and gratuities',
                'requirements': 'Valid passport, Yellow fever certificate, Comfortable safari clothing, Sun protection, Camera with extra batteries',
                'cancellation_policy': 'Free cancellation up to 14 days before departure. 50% refund for cancellations 7-14 days before. No refund for cancellations within 7 days.',
                'featured': True,
                'status': 'published'
            },
            {
                'title': 'Diani Beach Paradise Getaway',
                'slug': 'diani-beach-paradise-getaway',
                'description': 'Escape to the pristine white sands of Diani Beach, consistently rated among the world\'s best beaches. This 5-day coastal retreat offers the perfect blend of relaxation and adventure. Enjoy water sports, dhow sailing, visit Colobus monkeys at Colobus Trust, and indulge in fresh seafood cuisine. Stay at a beachfront resort with stunning ocean views.',
                'short_description': 'Relax on pristine Diani Beach with water sports and luxury beachfront accommodation',
                'event_type': 'beach',
                'category_slug': 'beach-holiday',
                'location_name': 'Diani Beach',
                'start_date': timezone.now() + timedelta(days=45),
                'duration_days': 5,
                'max_participants': 20,
                'min_participants': 1,
                'base_price': Decimal('32000'),
                'child_price': Decimal('24000'),
                'vip_price': Decimal('48000'),
                'group_discount_percentage': Decimal('8'),
                'includes': 'Beachfront accommodation, Daily breakfast, Airport transfers, Dhow sailing trip, Snorkeling equipment, Colobus Trust visit, Welcome cocktail',
                'excludes': 'Lunch and dinner, Water sports activities, Spa treatments, Personal expenses, Travel insurance',
                'requirements': 'Valid ID, Swimwear, Sun protection, Comfortable clothing',
                'cancellation_policy': 'Free cancellation up to 7 days before check-in. 50% refund for cancellations 3-7 days before.',
                'featured': True,
                'status': 'published'
            },
            {
                'title': 'Mount Kenya Climbing Expedition',
                'slug': 'mount-kenya-climbing-expedition',
                'description': 'Conquer Africa\'s second highest peak on this challenging 6-day climbing expedition. Follow the Sirimon route to Point Lenana (4,985m) through diverse ecosystems from bamboo forests to alpine zones. Experience breathtaking sunrise views, unique high-altitude vegetation, and the satisfaction of reaching the summit. Professional mountain guides ensure safety throughout the journey.',
                'short_description': 'Climb Mount Kenya to Point Lenana with professional guides and mountain huts',
                'event_type': 'mountain',
                'category_slug': 'mountain-climbing',
                'location_name': 'Mount Kenya',
                'start_date': timezone.now() + timedelta(days=60),
                'duration_days': 6,
                'max_participants': 12,
                'min_participants': 4,
                'base_price': Decimal('55000'),
                'child_price': None,  # Age restrictions apply
                'vip_price': Decimal('75000'),
                'group_discount_percentage': Decimal('12'),
                'includes': 'Professional mountain guides, Porters, Mountain hut accommodation, All meals, Climbing equipment, Park fees, Transportation from Nairobi, Certificate of achievement',
                'excludes': 'Personal climbing gear, Sleeping bag, Travel insurance, Personal medication, Tips for guides and porters',
                'requirements': 'Age 16+, Good physical fitness, Medical clearance, Proper hiking boots, Warm clothing for high altitude',
                'cancellation_policy': 'Free cancellation up to 21 days before climb. 25% refund for cancellations 14-21 days before.',
                'featured': True,
                'status': 'published'
            },
            {
                'title': 'Samburu Cultural and Wildlife Experience',
                'slug': 'samburu-cultural-wildlife-experience',
                'description': 'Discover the unique culture of the Samburu people while enjoying exceptional wildlife viewing in one of Kenya\'s most scenic reserves. This 4-day experience combines game drives to see the special five (Grevy\'s zebra, reticulated giraffe, Beisa oryx, Somali ostrich, and gerenuk) with authentic cultural interactions including traditional dances, beadwork, and learning about Samburu customs.',
                'short_description': 'Experience Samburu wildlife and authentic cultural interactions with local communities',
                'event_type': 'cultural',
                'category_slug': 'cultural-experience',
                'location_name': 'Samburu National Reserve',
                'start_date': timezone.now() + timedelta(days=75),
                'duration_days': 4,
                'max_participants': 16,
                'min_participants': 2,
                'base_price': Decimal('42000'),
                'child_price': Decimal('32000'),
                'vip_price': Decimal('58000'),
                'group_discount_percentage': Decimal('10'),
                'includes': 'Safari lodge accommodation, All meals, Game drives, Cultural village visit, Traditional performances, Professional guide, Transportation, Park fees',
                'excludes': 'Personal expenses, Alcoholic beverages, Travel insurance, Tips, Souvenirs',
                'requirements': 'Respectful clothing for cultural visits, Sun protection, Camera, Valid passport',
                'cancellation_policy': 'Free cancellation up to 10 days before departure. 50% refund for cancellations 5-10 days before.',
                'featured': False,
                'status': 'published'
            },
            {
                'title': 'Lake Nakuru Flamingo Spectacular',
                'slug': 'lake-nakuru-flamingo-spectacular',
                'description': 'Visit Lake Nakuru National Park, famous for its massive flocks of flamingos that create a pink shoreline. This 3-day safari also offers excellent opportunities to see both black and white rhinos, Rothschild giraffes, lions, and over 400 bird species. The park\'s scenic beauty includes waterfalls, cliffs, and the shimmering soda lake.',
                'short_description': 'See millions of flamingos at Lake Nakuru plus rhinos and diverse wildlife',
                'event_type': 'safari',
                'category_slug': 'wildlife-safari',
                'location_name': 'Lake Nakuru',
                'start_date': timezone.now() + timedelta(days=25),
                'duration_days': 3,
                'max_participants': 18,
                'min_participants': 2,
                'base_price': Decimal('28000'),
                'child_price': Decimal('21000'),
                'vip_price': Decimal('38000'),
                'group_discount_percentage': Decimal('8'),
                'includes': 'Lodge accommodation, All meals, Game drives, Park fees, Professional guide, Transportation from Nairobi',
                'excludes': 'Personal expenses, Travel insurance, Tips, Alcoholic beverages',
                'requirements': 'Valid ID, Comfortable safari clothing, Binoculars, Camera',
                'cancellation_policy': 'Free cancellation up to 7 days before departure.',
                'featured': False,
                'status': 'published'
            },
            {
                'title': 'Great Rift Valley Road Trip Adventure',
                'slug': 'great-rift-valley-road-trip-adventure',
                'description': 'Explore the dramatic landscapes of the Great Rift Valley on this 7-day road trip adventure. Drive through scenic highlands, visit multiple lakes, experience local markets, and enjoy diverse landscapes from escarpments to crater lakes. This self-drive experience includes stops at Lake Naivasha, Hell\'s Gate, Lake Nakuru, and traditional Maasai markets.',
                'short_description': 'Self-drive adventure through the scenic Great Rift Valley with multiple stops',
                'event_type': 'road_trip',
                'category_slug': 'road-trip',
                'location_name': 'Lake Naivasha',
                'start_date': timezone.now() + timedelta(days=40),
                'duration_days': 7,
                'max_participants': 8,
                'min_participants': 2,
                'base_price': Decimal('48000'),
                'child_price': Decimal('35000'),
                'vip_price': Decimal('68000'),
                'group_discount_percentage': Decimal('15'),
                'includes': '4WD vehicle rental, Fuel, Accommodation, Daily breakfast, Route planning, Emergency support, Park fees, Local guide at key stops',
                'excludes': 'International driving permit, Personal meals (except breakfast), Personal expenses, Travel insurance',
                'requirements': 'Valid driving license, International driving permit, Age 23+, Driving experience',
                'cancellation_policy': 'Free cancellation up to 14 days before departure. 25% refund for cancellations 7-14 days before.',
                'featured': False,
                'status': 'published'
            },
            {
                'title': 'Watamu Marine Park Snorkeling Safari',
                'slug': 'watamu-marine-park-snorkeling-safari',
                'description': 'Discover the underwater wonders of Watamu Marine National Park, home to Kenya\'s most pristine coral reefs. This 4-day marine adventure includes snorkeling in crystal-clear waters, turtle watching at Local Ocean Trust, dolphin spotting trips, and relaxation on beautiful beaches. Perfect for water enthusiasts and marine life lovers.',
                'short_description': 'Explore Watamu\'s coral reefs with snorkeling, turtle watching, and dolphin trips',
                'event_type': 'adventure',
                'category_slug': 'adventure-sports',
                'location_name': 'Watamu',
                'start_date': timezone.now() + timedelta(days=55),
                'duration_days': 4,
                'max_participants': 14,
                'min_participants': 2,
                'base_price': Decimal('35000'),
                'child_price': Decimal('28000'),
                'vip_price': Decimal('48000'),
                'group_discount_percentage': Decimal('10'),
                'includes': 'Beachfront accommodation, Daily breakfast, Snorkeling equipment, Boat trips, Marine park fees, Professional guide, Turtle sanctuary visit',
                'excludes': 'Lunch and dinner, Personal expenses, Travel insurance, Underwater camera rental',
                'requirements': 'Basic swimming ability, Valid ID, Swimwear, Sun protection',
                'cancellation_policy': 'Free cancellation up to 5 days before departure.',
                'featured': False,
                'status': 'published'
            },
            {
                'title': 'Lamu Island Cultural Heritage Tour',
                'slug': 'lamu-island-cultural-heritage-tour',
                'description': 'Step back in time on Lamu Island, a UNESCO World Heritage site where Swahili culture thrives unchanged for centuries. This 5-day cultural immersion includes exploring Stone Town\'s narrow streets, visiting museums, dhow sailing, traditional Swahili cooking classes, and experiencing the island\'s unique donkey transportation system.',
                'short_description': 'UNESCO World Heritage Lamu Island with Swahili culture and dhow sailing',
                'event_type': 'cultural',
                'category_slug': 'cultural-experience',
                'location_name': 'Lamu Island',
                'start_date': timezone.now() + timedelta(days=70),
                'duration_days': 5,
                'max_participants': 12,
                'min_participants': 2,
                'base_price': Decimal('38000'),
                'child_price': Decimal('30000'),
                'vip_price': Decimal('52000'),
                'group_discount_percentage': Decimal('12'),
                'includes': 'Traditional Swahili house accommodation, Daily breakfast, Dhow sailing, Museum visits, Cooking class, Local guide, Domestic flights from Nairobi',
                'excludes': 'Lunch and dinner, Personal expenses, Travel insurance, Shopping, Tips',
                'requirements': 'Respectful clothing, Valid passport, Cultural sensitivity',
                'cancellation_policy': 'Free cancellation up to 10 days before departure.',
                'featured': True,
                'status': 'published'
            }
        ]
        
        for event_data in events_data:
            category = Category.objects.get(slug=event_data['category_slug'])
            location = Location.objects.get(name=event_data['location_name'])
            
            start_date = event_data['start_date']
            end_date = start_date + timedelta(days=event_data['duration_days'])
            booking_deadline = start_date - timedelta(days=3)
            
            event, created = Event.objects.get_or_create(
                slug=event_data['slug'],
                defaults={
                    'title': event_data['title'],
                    'description': event_data['description'],
                    'short_description': event_data['short_description'],
                    'event_type': event_data['event_type'],
                    'category': category,
                    'location': location,
                    'start_date': start_date,
                    'end_date': end_date,
                    'duration_days': event_data['duration_days'],
                    'max_participants': event_data['max_participants'],
                    'min_participants': event_data['min_participants'],
                    'current_bookings': random.randint(0, event_data['max_participants'] // 2),
                    'base_price': event_data['base_price'],
                    'child_price': event_data['child_price'],
                    'vip_price': event_data['vip_price'],
                    'group_discount_percentage': event_data['group_discount_percentage'],
                    'includes': event_data['includes'],
                    'excludes': event_data['excludes'],
                    'requirements': event_data['requirements'],
                    'booking_deadline': booking_deadline,
                    'cancellation_policy': event_data['cancellation_policy'],
                    'whatsapp_booking': True,
                    'online_payment': True,
                    'status': event_data['status'],
                    'featured': event_data['featured'],
                    'created_by': admin_user
                }
            )
            
            # Add event features
            if created:
                features = EventFeature.objects.all()
                for feature in random.sample(list(features), k=random.randint(4, 8)):
                    EventFeatureAssignment.objects.create(
                        event=event,
                        feature=feature,
                        is_included=True,
                        notes=f"Included in {event.title}"
                    )
        
        self.stdout.write('✓ Events created')

    def create_pricing_tiers(self):
        """Create pricing tiers for events"""
        events = Event.objects.all()
        
        for event in events:
            # Regular tier
            PricingTier.objects.get_or_create(
                event=event,
                tier_type='regular',
                defaults={
                    'name': 'Regular Package',
                    'description': 'Standard accommodation and services',
                    'price': event.base_price,
                    'max_capacity': event.max_participants // 2,
                    'current_bookings': random.randint(0, event.max_participants // 4),
                    'features': 'Standard accommodation, All meals, Transportation, Professional guide',
                    'is_active': True
                }
            )
            
            # VIP tier (if VIP price exists)
            if event.vip_price:
                PricingTier.objects.get_or_create(
                    event=event,
                    tier_type='vip',
                    defaults={
                        'name': 'VIP Experience',
                        'description': 'Luxury accommodation with premium services',
                        'price': event.vip_price,
                        'max_capacity': event.max_participants // 3,
                        'current_bookings': random.randint(0, event.max_participants // 6),
                        'features': 'Luxury accommodation, Gourmet meals, Private transportation, Personal guide, Premium activities',
                        'is_active': True
                    }
                )
        
        self.stdout.write('✓ Pricing tiers created')

    def create_faqs(self):
        """Create FAQs for events"""
        events = Event.objects.all()
        
        faq_templates = [
            {
                'question': 'What is included in the package price?',
                'answer': 'The package includes accommodation, specified meals, transportation, professional guide, and park/activity fees as detailed in the inclusions section.'
            },
            {
                'question': 'What should I pack for this trip?',
                'answer': 'Pack comfortable clothing suitable for the climate, sun protection, camera, personal medications, and any specific items mentioned in the requirements section.'
            },
            {
                'question': 'Is travel insurance required?',
                'answer': 'While not mandatory, we highly recommend comprehensive travel insurance to cover medical emergencies, trip cancellation, and personal belongings.'
            },
            {
                'question': 'What is the cancellation policy?',
                'answer': 'Please refer to our cancellation policy for specific terms and conditions regarding refunds and timing requirements.'
            },
            {
                'question': 'Are there age restrictions for this experience?',
                'answer': 'Age requirements vary by activity type. Please check the requirements section or contact us for specific age-related information.'
            },
            {
                'question': 'How do I make payment?',
                'answer': 'We accept M-Pesa, bank transfers, and credit cards. You can pay online during booking or via WhatsApp booking process.'
            },
            {
                'question': 'What happens in case of bad weather?',
                'answer': 'We monitor weather conditions closely and will adjust itineraries as needed for safety while ensuring you still have an amazing experience.'
            },
            {
                'question': 'Can dietary requirements be accommodated?',
                'answer': 'Yes, we can accommodate most dietary requirements including vegetarian, vegan, and religious dietary needs. Please inform us during booking.'
            }
        ]
        
        for event in events[:5]:  # Add FAQs to first 5 events
            for i, faq_data in enumerate(faq_templates):
                FAQ.objects.get_or_create(
                    event=event,
                    question=faq_data['question'],
                    defaults={
                        'answer': faq_data['answer'],
                        'order': i + 1,
                        'is_active': True
                    }
                )
        
        self.stdout.write('✓ FAQs created')

    def create_itineraries(self):
        """Create detailed itineraries for events"""
        events = Event.objects.all()
        
        # Sample itinerary templates for different event types
        safari_itinerary = [
            {
                'day': 1,
                'title': 'Arrival and First Game Drive',
                'description': 'Arrive at the destination, check into accommodation, and enjoy an afternoon game drive.',
                'activities': 'Airport pickup, lodge check-in, welcome briefing, afternoon game drive, dinner',
                'meals': 'L, D',
                'accommodation': 'Safari Lodge'
            },
            {
                'day': 2,
                'title': 'Full Day Game Viewing',
                'description': 'Full day exploring the park with morning and afternoon game drives.',
                'activities': 'Early morning game drive, breakfast in the bush, afternoon game drive, evening at leisure',
                'meals': 'B, L, D',
                'accommodation': 'Safari Lodge'
            },
            {
                'day': 3,
                'title': 'Cultural Visit and Game Drive',
                'description': 'Visit local community and enjoy final game drive before departure.',
                'activities': 'Morning cultural visit, final game drive, lunch, departure preparation',
                'meals': 'B, L',
                'accommodation': 'N/A'
            }
        ]
        
        beach_itinerary = [
            {
                'day': 1,
                'title': 'Arrival and Beach Relaxation',
                'description': 'Arrive at the beach destination and settle into your beachfront accommodation.',
                'activities': 'Airport transfer, hotel check-in, welcome drink, beach walk, sunset viewing',
                'meals': 'D',
                'accommodation': 'Beachfront Resort'
            },
            {
                'day': 2,
                'title': 'Water Sports and Marine Activities',
                'description': 'Enjoy various water sports and marine activities.',
                'activities': 'Snorkeling trip, dhow sailing, beach games, spa treatment (optional)',
                'meals': 'B',
                'accommodation': 'Beachfront Resort'
            },
            {
                'day': 3,
                'title': 'Cultural Exploration',
                'description': 'Explore local culture and attractions.',
                'activities': 'Local market visit, cultural site tour, traditional lunch, craft shopping',
                'meals': 'B, L',
                'accommodation': 'Beachfront Resort'
            }
        ]
        
        mountain_itinerary = [
            {
                'day': 1,
                'title': 'Base Camp Arrival',
                'description': 'Arrive at the base and prepare for climbing expedition.',
                'activities': 'Equipment check, briefing session, acclimatization walk, early rest',
                'meals': 'B, L, D',
                'accommodation': 'Mountain Hut'
            },
            {
                'day': 2,
                'title': 'Ascent Day 1',
                'description': 'Begin the ascent through changing vegetation zones.',
                'activities': 'Early morning start, trekking through forest zone, camp setup',
                'meals': 'B, L, D',
                'accommodation': 'Mountain Hut'
            },
            {
                'day': 3,
                'title': 'Summit Attempt',
                'description': 'Early morning summit attempt and descent.',
                'activities': 'Pre-dawn start, summit attempt, celebration, descent to base',
                'meals': 'B, L, D',
                'accommodation': 'Mountain Hut'
            }
        ]
        
        # Apply itineraries based on event type
        for event in events:
            if event.event_type in ['safari']:
                itinerary_template = safari_itinerary[:event.duration_days]
            elif event.event_type in ['beach']:
                itinerary_template = beach_itinerary[:event.duration_days]
            elif event.event_type in ['mountain']:
                itinerary_template = mountain_itinerary[:event.duration_days]
            else:
                # Generic itinerary for other types
                itinerary_template = [
                    {
                        'day': i + 1,
                        'title': f'Day {i + 1} - {event.title} Activities',
                        'description': f'Enjoy day {i + 1} of your {event.title} experience.',
                        'activities': 'Planned activities as per event schedule',
                        'meals': 'B, L, D' if i > 0 else 'L, D',
                        'accommodation': 'As per booking'
                    }
                    for i in range(event.duration_days)
                ]
            
            for day_data in itinerary_template:
                Itinerary.objects.get_or_create(
                    event=event,
                    day_number=day_data['day'],
                    defaults={
                        'title': day_data['title'],
                        'description': day_data['description'],
                        'activities': day_data['activities'],
                        'meals_included': day_data['meals'],
                        'accommodation': day_data['accommodation']
                    }
                )
        
        self.stdout.write('✓ Itineraries created')

    def create_bookings(self):
        """Create sample bookings"""
        events = Event.objects.filter(status='published')
        
        # Sample Kenyan customer data
        customers_data = [
            {
                'name': 'Jane Wanjiku Mwangi',
                'email': 'jane.mwangi@gmail.com',
                'phone': '+254722345678',
                'address': 'Kiambu Road, Nairobi'
            },
            {
                'name': 'David Kipchoge Rotich',
                'email': 'david.rotich@yahoo.com',
                'phone': '+254733456789',
                'address': 'Eldoret, Uasin Gishu County'
            },
            {
                'name': 'Grace Akinyi Ochieng',
                'email': 'grace.ochieng@outlook.com',
                'phone': '+254744567890',
                'address': 'Kisumu, Kisumu County'
            },
            {
                'name': 'Samuel Mwenda Muthomi',
                'email': 'samuel.muthomi@gmail.com',
                'phone': '+254755678901',
                'address': 'Meru, Meru County'
            },
            {
                'name': 'Catherine Wambui Kamau',
                'email': 'catherine.kamau@hotmail.com',
                'phone': '+254766789012',
                'address': 'Nakuru, Nakuru County'
            },
            {
                'name': 'Peter Omondi Otieno',
                'email': 'peter.otieno@gmail.com',
                'phone': '+254777890123',
                'address': 'Mombasa, Mombasa County'
            }
        ]
        
        booking_methods = ['online', 'whatsapp', 'phone', 'email']
        booking_statuses = ['confirmed', 'paid', 'pending', 'completed']
        
        for i in range(15):  # Create 15 sample bookings
            event = random.choice(events)
            customer = random.choice(customers_data)
            participants = random.randint(1, min(4, event.max_participants - event.current_bookings))
            
            if participants <= 0:
                continue
            
            adults = random.randint(1, participants)
            children = participants - adults
            
            base_amount = event.base_price * adults
            if children > 0 and event.child_price:
                base_amount += event.child_price * children
            
            discount = Decimal('0')
            if participants >= 4:  # Group discount
                discount = base_amount * (event.group_discount_percentage / 100)
            
            tax_amount = (base_amount - discount) * Decimal('0.16')  # 16% VAT in Kenya
            total_amount = base_amount - discount + tax_amount
            
            booking = Booking.objects.create(
                event=event,
                customer_name=customer['name'],
                customer_email=customer['email'],
                customer_phone=customer['phone'],
                customer_address=customer['address'],
                emergency_contact_name=f"Emergency Contact for {customer['name']}",
                emergency_contact_phone='+254700000000',
                number_of_participants=participants,
                adults_count=adults,
                children_count=children,
                base_amount=base_amount,
                discount_amount=discount,
                tax_amount=tax_amount,
                total_amount=total_amount,
                booking_method=random.choice(booking_methods),
                status=random.choice(booking_statuses),
                special_requests=random.choice([
                    '', 'Vegetarian meals please', 'Ground floor room preferred',
                    'Celebrating anniversary', 'First time safari'
                ]),
                dietary_requirements=random.choice([
                    '', 'Vegetarian', 'No pork', 'Gluten-free', 'Diabetic meals'
                ])
            )
            
            # Create booking participants
            participant_names = [
                'John Doe', 'Mary Smith', 'Peter Parker', 'Jane Watson',
                'Michael Johnson', 'Sarah Wilson', 'David Brown', 'Lisa Davis'
            ]
            
            for j in range(participants):
                participant_type = 'adult' if j < adults else 'child'
                age = random.randint(25, 65) if participant_type == 'adult' else random.randint(5, 17)
                
                BookingParticipant.objects.create(
                    booking=booking,
                    name=random.choice(participant_names),
                    age=age,
                    participant_type=participant_type,
                    id_number=f'{random.randint(10000000, 99999999)}' if participant_type == 'adult' else '',
                    medical_conditions=random.choice(['', 'None', 'Hypertension', 'Diabetes'])
                )
            
            # Update event booking count
            event.current_bookings += participants
            event.save()
        
        self.stdout.write('✓ Sample bookings created')

    def create_payments(self):
        """Create payment records for bookings"""
        bookings = Booking.objects.all()
        
        payment_methods = ['mpesa', 'bank_transfer', 'card']
        payment_statuses = ['completed', 'pending', 'processing', 'failed']
        
        for booking in bookings:
            # 80% chance of having a payment record
            if random.random() < 0.8:
                payment_method = random.choice(payment_methods)
                payment_status = random.choice(payment_statuses)
                
                # If booking is paid, payment should be completed
                if booking.status == 'paid':
                    payment_status = 'completed'
                
                payment = Payment.objects.create(
                    booking=booking,
                    payment_id=f'WQ{random.randint(100000, 999999)}',
                    amount=booking.total_amount,
                    payment_method=payment_method,
                    status=payment_status,
                    transaction_reference=f'TXN{random.randint(1000000, 9999999)}',
                    initiated_at=booking.booked_at + timedelta(minutes=random.randint(1, 60))
                )
                
                # M-Pesa specific fields
                if payment_method == 'mpesa':
                    payment.mpesa_checkout_id = f'ws_CO_{random.randint(100000000, 999999999)}'
                    payment.mpesa_phone_number = booking.customer_phone
                    if payment_status == 'completed':
                        payment.mpesa_transaction_id = f'QG{random.randint(10000000, 99999999)}'
                        payment.completed_at = payment.initiated_at + timedelta(minutes=random.randint(1, 10))
                
                payment.save()
        
        self.stdout.write('✓ Payment records created')

    def create_reviews(self):
        """Create customer reviews"""
        completed_bookings = Booking.objects.filter(status__in=['completed', 'paid'])
        
        review_titles = [
            'Amazing Experience!',
            'Unforgettable Safari Adventure',
            'Perfect Beach Holiday',
            'Excellent Service and Guides',
            'Great Value for Money',
            'Beautiful Destinations',
            'Professional Organization',
            'Highly Recommended!',
            'Exceeded Expectations',
            'Wonderful Cultural Experience'
        ]
        
        review_comments = [
            'Had an absolutely fantastic time! The guides were knowledgeable and the accommodation was excellent. Would definitely book again.',
            'This was our first safari and it exceeded all expectations. Saw the Big Five and the Great Migration. Truly spectacular!',
            'Perfect organization from start to finish. The team at WildQuest made everything seamless and enjoyable.',
            'Beautiful locations and great value for money. The cultural interactions were authentic and respectful.',
            'The beach was pristine and the resort was perfect. Great for families and couples alike.',
            'Professional guides who really know their stuff. Learned so much about Kenyan wildlife and culture.',
            'Everything was well-organized and on time. No hassles, just pure enjoyment of Kenya\'s beauty.',
            'Amazing experience climbing Mount Kenya. Challenging but the guides helped us reach the summit safely.',
            'The dhow sailing and snorkeling were highlights. Marine life was incredible at Watamu.',
            'Authentic Kenyan experience with great food, friendly people, and stunning scenery.'
        ]
        
        for booking in completed_bookings[:10]:  # Create reviews for first 10 completed bookings
            if random.random() < 0.7:  # 70% chance of having a review
                Review.objects.create(
                    event=booking.event,
                    booking=booking,
                    reviewer_name=booking.customer_name,
                    reviewer_email=booking.customer_email,
                    rating=random.choices([5, 4, 3, 2, 1], weights=[50, 30, 15, 4, 1])[0],
                    title=random.choice(review_titles),
                    comment=random.choice(review_comments),
                    is_verified=True,
                    is_approved=random.choice([True, True, True, False]),  # 75% approved
                    created_at=booking.booked_at + timedelta(days=random.randint(1, 30))
                )
        
        self.stdout.write('✓ Customer reviews created')

    def create_whatsapp_bookings(self):
        """Create WhatsApp booking requests"""
        events = Event.objects.filter(status='published')
        admin_user = User.objects.get(username='admin')
        
        whatsapp_messages = [
            {
                'customer_name': 'Faith Njeri',
                'phone': '+254721234567',
                'message': 'Hi, I\'m interested in the Maasai Mara safari for 3 people from March 15-18. Can you send me more details and pricing?',
                'participants': 3
            },
            {
                'customer_name': 'Robert Kimani',
                'phone': '+254732345678',
                'message': 'Hello WildQuest! Looking for a beach holiday package for 2 adults and 2 children. Diani Beach preferred. What are your rates?',
                'participants': 4
            },
            {
                'customer_name': 'Agnes Moraa',
                'phone': '+254743456789',
                'message': 'Good morning. I want to climb Mount Kenya next month. Do you have availability for 2 people? What\'s included in the package?',
                'participants': 2
            },
            {
                'customer_name': 'Daniel Kiprotich',
                'phone': '+254754567890',
                'message': 'Habari! I need information about Samburu cultural tour. We are 6 people from church group. Group rates available?',
                'participants': 6
            },
            {
                'customer_name': 'Caroline Waweru',
                'phone': '+254765678901',
                'message': 'Hi there! Planning honeymoon trip to Watamu. Need romantic package for 2 with snorkeling activities. Please advise.',
                'participants': 2
            }
        ]
        
        statuses = ['new', 'processing', 'processed']
        
        for msg_data in whatsapp_messages:
            event = random.choice(events)
            status = random.choice(statuses)
            
            whatsapp_booking = WhatsAppBooking.objects.create(
                event=event,
                customer_name=msg_data['customer_name'],
                customer_phone=msg_data['phone'],
                message=msg_data['message'],
                participants_count=msg_data['participants'],
                status=status,
                processed_by=admin_user if status != 'new' else None,
                processed_at=timezone.now() - timedelta(days=random.randint(1, 5)) if status != 'new' else None
            )
        
        self.stdout.write('✓ WhatsApp booking requests created')

    def create_contact_inquiries(self):
        """Create contact form submissions"""
        events = Event.objects.all()
        admin_user = User.objects.get(username='admin')
        
        inquiries_data = [
            {
                'name': 'James Maina',
                'email': 'james.maina@company.co.ke',
                'phone': '+254776543210',
                'type': 'general',
                'subject': 'Corporate Team Building Packages',
                'message': 'We are looking for team building packages for 25 employees. Can you recommend suitable destinations and activities?'
            },
            {
                'name': 'Susan Adhiambo',
                'email': 'susan.adhiambo@gmail.com',
                'phone': '+254787654321',
                'type': 'booking',
                'subject': 'Group Booking Discount Inquiry',
                'message': 'Planning a family reunion with 15 people. What group discounts do you offer for safari packages?'
            },
            {
                'name': 'Michael Wanyama',
                'email': 'mike.wanyama@yahoo.com',
                'phone': '+254798765432',
                'type': 'support',
                'subject': 'Booking Confirmation Issue',
                'message': 'I made a booking last week but haven\'t received confirmation email. Booking reference WQ123456.'
            },
            {
                'name': 'Elizabeth Mutua',
                'email': 'liz.mutua@outlook.com',
                'phone': '',
                'type': 'feedback',
                'subject': 'Excellent Service Feedback',
                'message': 'Just completed the Diani Beach package and wanted to commend your team for excellent service!'
            },
            {
                'name': 'Patrick Oduya',
                'email': 'patrick.oduya@tourism.go.ke',
                'phone': '+254701234567',
                'type': 'partnership',
                'subject': 'Tourism Board Partnership',
                'message': 'Kenya Tourism Board is interested in partnering with WildQuest for promoting domestic tourism.'
            }
        ]
        
        for inquiry_data in inquiries_data:
            is_resolved = random.choice([True, False])
            event = random.choice([None, random.choice(events)])
            
            ContactInquiry.objects.create(
                name=inquiry_data['name'],
                email=inquiry_data['email'],
                phone=inquiry_data['phone'],
                inquiry_type=inquiry_data['type'],
                subject=inquiry_data['subject'],
                message=inquiry_data['message'],
                event=event,
                is_resolved=is_resolved,
                resolved_by=admin_user if is_resolved else None,
                resolved_at=timezone.now() - timedelta(days=random.randint(1, 7)) if is_resolved else None,
                admin_notes='Issue resolved via phone call' if is_resolved else '',
                created_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )
        
        self.stdout.write('✓ Contact inquiries created')

    def create_newsletter_subscriptions(self):
        """Create newsletter subscriptions"""
        subscribers_data = [
            {'email': 'mary.wanjiru@gmail.com', 'name': 'Mary Wanjiru'},
            {'email': 'john.kamau@yahoo.com', 'name': 'John Kamau'},
            {'email': 'grace.auma@outlook.com', 'name': 'Grace Auma'},
            {'email': 'peter.mwangi@company.com', 'name': 'Peter Mwangi'},
            {'email': 'jane.waweru@gmail.com', 'name': 'Jane Waweru'},
            {'email': 'david.kibet@hotmail.com', 'name': 'David Kibet'},
            {'email': 'sarah.nyong@gmail.com', 'name': 'Sarah Nyong'},
            {'email': 'anthony.muthee@yahoo.com', 'name': 'Anthony Muthee'},
            {'email': 'florence.atieno@outlook.com', 'name': 'Florence Atieno'},
            {'email': 'samuel.kiprop@gmail.com', 'name': 'Samuel Kiprop'},
            {'email': 'rachel.wambui@company.co.ke', 'name': 'Rachel Wambui'},
            {'email': 'joseph.mutua@hotmail.com', 'name': 'Joseph Mutua'},
            {'email': 'esther.chebet@gmail.com', 'name': 'Esther Chebet'},
            {'email': 'francis.otieno@yahoo.com', 'name': 'Francis Otieno'},
            {'email': 'margaret.njoki@outlook.com', 'name': 'Margaret Njoki'}
        ]
        
        for subscriber_data in subscribers_data:
            NewsletterSubscription.objects.get_or_create(
                email=subscriber_data['email'],
                defaults={
                    'name': subscriber_data['name'],
                    'is_active': random.choice([True, True, True, False]),  # 75% active
                    'subscribed_at': timezone.now() - timedelta(days=random.randint(1, 100))
                }
            )
        
        self.stdout.write('✓ Newsletter subscriptions created')

    def create_system_configurations(self):
        """Create system-wide configuration settings"""
        configurations = [
            {
                'key': 'SITE_NAME',
                'value': 'WildQuest Kenya',
                'description': 'Main site name displayed across the platform'
            },
            {
                'key': 'CONTACT_EMAIL',
                'value': 'info@wildquest.co.ke',
                'description': 'Primary contact email for customer inquiries'
            },
            {
                'key': 'CONTACT_PHONE',
                'value': '+254700123456',
                'description': 'Primary contact phone number'
            },
            {
                'key': 'WHATSAPP_NUMBER',
                'value': '+254700123456',
                'description': 'WhatsApp number for booking inquiries'
            },
            {
                'key': 'OFFICE_ADDRESS',
                'value': 'Westlands, Nairobi, Kenya',
                'description': 'Physical office address'
            },
            {
                'key': 'MPESA_SHORTCODE',
                'value': '174379',
                'description': 'M-Pesa business shortcode for payments'
            },
            {
                'key': 'BOOKING_TERMS',
                'value': 'All bookings are subject to availability and terms and conditions. Payment confirmation required within 24 hours.',
                'description': 'Standard booking terms and conditions'
            },
            {
                'key': 'CANCELLATION_POLICY',
                'value': 'Free cancellation up to 7 days before travel date. 50% refund for cancellations 3-7 days before.',
                'description': 'Default cancellation policy'
            },
            {
                'key': 'MAX_GROUP_SIZE',
                'value': '50',
                'description': 'Maximum group size for events'
            },
            {
                'key': 'ADVANCE_BOOKING_DAYS',
                'value': '3',
                'description': 'Minimum days required for advance booking'
            },
            {
                'key': 'TAX_RATE',
                'value': '0.16',
                'description': 'VAT rate applied to bookings (16% in Kenya)'
            },
            {
                'key': 'CURRENCY',
                'value': 'KES',
                'description': 'Primary currency (Kenyan Shillings)'
            }
        ]
        
        for config in configurations:
            SystemConfiguration.objects.get_or_create(
                key=config['key'],
                defaults={
                    'value': config['value'],
                    'description': config['description'],
                    'is_active': True
                }
            )
        
        self.stdout.write('✓ System configurations created')

    def handle_success_message(self):
        """Display completion summary"""
        stats = {
            'Categories': Category.objects.count(),
            'Locations': Location.objects.count(),
            'Events': Event.objects.count(),
            'Event Features': EventFeature.objects.count(),
            'Bookings': Booking.objects.count(),
            'Payments': Payment.objects.count(),
            'Reviews': Review.objects.count(),
            'WhatsApp Requests': WhatsAppBooking.objects.count(),
            'Contact Inquiries': ContactInquiry.objects.count(),
            'Newsletter Subscribers': NewsletterSubscription.objects.count(),
            'System Configurations': SystemConfiguration.objects.count()
        }
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('🎉 WILDQUEST DATABASE SEEDING COMPLETED! 🎉'))
        self.stdout.write('='*50)
        
        self.stdout.write('\n📊 SEEDING SUMMARY:')
        for model_name, count in stats.items():
            self.stdout.write(f'  ✓ {model_name}: {count} records')
        
        self.stdout.write('\n🔐 ADMIN ACCESS:')
        self.stdout.write(f'  Username: admin')
        self.stdout.write(f'  Password: wildquest2024')
        self.stdout.write(f'  Email: steve.ongera@wildquest.co.ke')
        
        self.stdout.write('\n🌐 NEXT STEPS:')
        self.stdout.write('  1. Run: python manage.py runserver')
        self.stdout.write('  2. Visit: http://localhost:8000/admin')
        self.stdout.write('  3. Login with admin credentials above')
        self.stdout.write('  4. Explore the populated WildQuest platform!')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('🇰🇪 WildQuest - Discover Kenya\'s Wild Beauty! 🇰🇪'))
        self.stdout.write(self.style.SUCCESS('Developed by Steve Ongera'))
        self.stdout.write('='*50 + '\n')