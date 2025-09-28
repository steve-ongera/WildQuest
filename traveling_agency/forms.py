from django import forms
from django.core.validators import EmailValidator
from .models import (
    Booking, ContactInquiry, Review, NewsletterSubscription,
    PricingTier, BookingParticipant
)

class BookingForm(forms.ModelForm):
    """Form for creating bookings"""
    pricing_tier = forms.ModelChoiceField(
        queryset=PricingTier.objects.none(),
        required=False,
        empty_label="Select pricing tier (optional)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Booking
        fields = [
            'customer_name', 'customer_email', 'customer_phone', 
            'customer_address', 'emergency_contact_name', 'emergency_contact_phone',
            'adults_count', 'children_count', 'booking_method',
            'special_requests', 'dietary_requirements'
        ]
        
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+254 712 345 678'
            }),
            'customer_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Your address (optional)'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact phone'
            }),
            'adults_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1
            }),
            'children_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'value': 0
            }),
            'booking_method': forms.Select(attrs={
                'class': 'form-control'
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requests or requirements...'
            }),
            'dietary_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any dietary requirements or allergies...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        
        if self.event:
            # Filter pricing tiers for this event
            self.fields['pricing_tier'].queryset = self.event.pricing_tiers.filter(
                is_active=True
            )
            
            # Set default booking method
            if self.event.whatsapp_booking and not self.event.online_payment:
                self.fields['booking_method'].initial = 'whatsapp'
            elif self.event.online_payment:
                self.fields['booking_method'].initial = 'online'
    
    def clean(self):
        cleaned_data = super().clean()
        adults_count = cleaned_data.get('adults_count', 0)
        children_count = cleaned_data.get('children_count', 0)
        total_participants = adults_count + children_count
        
        if self.event:
            # Check minimum participants
            if total_participants < self.event.min_participants:
                raise forms.ValidationError(
                    f'Minimum {self.event.min_participants} participants required.'
                )
            
            # Check maximum participants
            if total_participants > self.event.max_participants:
                raise forms.ValidationError(
                    f'Maximum {self.event.max_participants} participants allowed.'
                )
            
            # Check available spots
            if total_participants > self.event.available_spots:
                raise forms.ValidationError(
                    f'Only {self.event.available_spots} spots available.'
                )
        
        return cleaned_data

class ContactForm(forms.ModelForm):
    """Contact form"""
    
    class Meta:
        model = ContactInquiry
        fields = [
            'name', 'email', 'phone', 'inquiry_type', 
            'subject', 'message', 'event'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+254 712 345 678'
            }),
            'inquiry_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject of your inquiry'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Your message...'
            }),
            'event': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make event field optional and show only published events
        from .models import Event
        self.fields['event'].queryset = Event.objects.filter(
            status='published'
        ).order_by('title')
        self.fields['event'].required = False
        self.fields['event'].empty_label = "Select an event (optional)"

class ReviewForm(forms.ModelForm):
    """Review form"""
    
    class Meta:
        model = Review
        fields = ['reviewer_name', 'reviewer_email', 'rating', 'title', 'comment']
        
        widgets = {
            'reviewer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name'
            }),
            'reviewer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com (optional)'
            }),
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review title'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reviewer_email'].required = False

class NewsletterForm(forms.ModelForm):
    """Newsletter subscription form"""
    
    class Meta:
        model = NewsletterSubscription
        fields = ['email', 'name']
        
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False

class EventSearchForm(forms.Form):
    """Event search and filter form"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search events, locations, or activities...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    event_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Booking.BOOKING_METHODS),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    location = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Locations",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min price'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max price'
        })
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    sort = forms.ChoiceField(
        choices=[
            ('date', 'Date (Earliest First)'),
            ('price', 'Price (Low to High)'),
            ('price_desc', 'Price (High to Low)'),
            ('popularity', 'Most Popular'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category, Location
        
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['location'].queryset = Location.objects.filter(
            event__status='published'
        ).distinct().order_by('name')

class ParticipantForm(forms.ModelForm):
    """Form for adding participants to a booking"""
    
    class Meta:
        model = BookingParticipant
        fields = ['name', 'age', 'participant_type', 'id_number', 'medical_conditions']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Participant name'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 120
            }),
            'participant_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'id_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ID/Passport number'
            }),
            'medical_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any medical conditions or allergies...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['age'].required = False
        self.fields['id_number'].required = False
        self.fields['medical_conditions'].required = False

class WhatsAppBookingForm(forms.Form):
    """Simple form for WhatsApp bookings"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name',
            'required': True
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+254 712 345 678',
            'required': True
        })
    )
    
    participants = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'value': 1,
            'min': 1
        })
    )
    
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any special requests or questions...'
        })
    )