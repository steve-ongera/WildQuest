from django import forms
from django.core.validators import EmailValidator, RegexValidator
from django.core.exceptions import ValidationError
from .models import (
    Booking, ContactInquiry, Review, NewsletterSubscription,
    PricingTier, BookingParticipant
)

class BookingForm(forms.ModelForm):
    """Form for creating bookings"""
    pricing_tier = forms.ModelChoiceField(
        queryset=PricingTier.objects.none(),
        required=False,
        empty_label="Regular Package",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'pricing_tier'
        })
    )
    
    # Phone number validator
    phone_validator = RegexValidator(
        regex=r'^\+?254\d{9}$|^0\d{9}$',
        message="Enter a valid Kenyan phone number (e.g., +254712345678 or 0712345678)"
    )
    
    class Meta:
        model = Booking
        fields = [
            'customer_name', 'customer_email', 'customer_phone',
            'adults_count', 'children_count', 'booking_method',
            'special_requests', 'dietary_requirements'
        ]
        
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'customer_name',
                'placeholder': 'Enter your full name',
                'required': True
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'id': 'customer_email',
                'placeholder': 'your.email@example.com',
                'required': True
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'customer_phone',
                'placeholder': '+254 712 345 678',
                'required': True
            }),
            'adults_count': forms.Select(attrs={
                'class': 'form-select',
                'id': 'adults_count',
                'required': True
            }),
            'children_count': forms.Select(attrs={
                'class': 'form-select',
                'id': 'children_count'
            }),
            'booking_method': forms.Select(attrs={
                'class': 'form-select',
                'id': 'booking_method',
                'required': True
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'special_requests',
                'rows': 3,
                'placeholder': 'Any special requests or requirements...'
            }),
            'dietary_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'dietary_requirements',
                'rows': 2,
                'placeholder': 'Any dietary requirements or allergies...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        
        # Add phone validator to the phone field
        self.fields['customer_phone'].validators = [self.phone_validator]
        
        # Set up adults count choices
        adults_choices = [('', 'Select adults')]
        for i in range(1, 11):
            adults_choices.append((i, str(i)))
        adults_choices.append((10, '10+'))
        self.fields['adults_count'].widget = forms.Select(
            choices=adults_choices,
            attrs=self.fields['adults_count'].widget.attrs
        )
        
        # Set up children count choices
        children_choices = [('0', '0')]
        for i in range(1, 10):
            children_choices.append((i, str(i)))
        self.fields['children_count'].widget = forms.Select(
            choices=children_choices,
            attrs=self.fields['children_count'].widget.attrs
        )
        
        if self.event:
            # Filter pricing tiers for this event
            self.fields['pricing_tier'].queryset = self.event.pricing_tiers.filter(
                is_active=True
            )
            
            # Set default booking method based on event preferences
            if self.event.whatsapp_booking and not self.event.online_payment:
                self.fields['booking_method'].initial = 'whatsapp'
            elif self.event.online_payment:
                self.fields['booking_method'].initial = 'online'
            
            # Hide children count if no child pricing
            if not self.event.child_price:
                self.fields['children_count'].widget = forms.HiddenInput()
                self.fields['children_count'].initial = 0
    
    def clean_customer_name(self):
        name = self.cleaned_data.get('customer_name')
        if name:
            name = name.strip()
            if len(name.split()) < 2:
                raise ValidationError('Please enter your full name (first and last name).')
        return name
    
    def clean_customer_email(self):
        email = self.cleaned_data.get('customer_email')
        if email:
            # Basic email validation is handled by EmailField
            # Add any additional validation here if needed
            return email.lower().strip()
        return email
    
    def clean_customer_phone(self):
        phone = self.cleaned_data.get('customer_phone')
        if phone:
            # Remove spaces and formatting
            phone = ''.join(phone.split())
            # Convert 07xx format to +254 format
            if phone.startswith('07') or phone.startswith('01'):
                phone = '+254' + phone[1:]
            elif phone.startswith('7') or phone.startswith('1'):
                phone = '+254' + phone
            return phone
        return phone
    
    def clean_adults_count(self):
        adults = self.cleaned_data.get('adults_count')
        if adults is None:
            raise ValidationError('Please select the number of adults.')
        try:
            adults = int(adults)
            if adults < 1:
                raise ValidationError('At least one adult is required.')
            if adults > 20:  # reasonable limit
                raise ValidationError('Maximum 20 adults allowed per booking.')
            return adults
        except (ValueError, TypeError):
            raise ValidationError('Please enter a valid number of adults.')
    
    def clean_children_count(self):
        children = self.cleaned_data.get('children_count', 0)
        try:
            children = int(children) if children else 0
            if children < 0:
                raise ValidationError('Number of children cannot be negative.')
            if children > 20:  # reasonable limit
                raise ValidationError('Maximum 20 children allowed per booking.')
            return children
        except (ValueError, TypeError):
            raise ValidationError('Please enter a valid number of children.')
    
    def clean(self):
        cleaned_data = super().clean()
        adults_count = cleaned_data.get('adults_count', 0)
        children_count = cleaned_data.get('children_count', 0)
        pricing_tier = cleaned_data.get('pricing_tier')
        
        try:
            adults_count = int(adults_count) if adults_count else 0
            children_count = int(children_count) if children_count else 0
        except (ValueError, TypeError):
            raise ValidationError('Invalid participant counts.')
        
        total_participants = adults_count + children_count
        
        if total_participants == 0:
            raise ValidationError('At least one participant is required.')
        
        if self.event:
            # Check minimum participants
            if total_participants < self.event.min_participants:
                raise ValidationError(
                    f'Minimum {self.event.min_participants} participants required for this event.'
                )
            
            # Check maximum participants for the event
            if total_participants > self.event.max_participants:
                raise ValidationError(
                    f'Maximum {self.event.max_participants} participants allowed for this event.'
                )
            
            # Check available spots
            if total_participants > self.event.available_spots:
                raise ValidationError(
                    f'Only {self.event.available_spots} spots available. Please reduce the number of participants.'
                )
            
            # Check pricing tier capacity if selected
            if pricing_tier and total_participants > pricing_tier.available_spots:
                raise ValidationError(
                    f'Only {pricing_tier.available_spots} spots available for {pricing_tier.name}.'
                )
        
        return cleaned_data


class ContactInquiryForm(forms.ModelForm):
    """Contact form"""
    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'phone', 'inquiry_type', 'subject', 'message', 'event']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'inquiry_type': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'event': forms.Select(attrs={'class': 'form-select'}),
        }


class ReviewForm(forms.ModelForm):
    """Review form"""
    class Meta:
        model = Review
        fields = ['reviewer_name', 'reviewer_email', 'rating', 'title', 'comment']
        
        widgets = {
            'reviewer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'reviewer_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)], 
                                 attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class NewsletterSubscriptionForm(forms.ModelForm):
    """Newsletter subscription form"""
    class Meta:
        model = NewsletterSubscription
        fields = ['email', 'name']
        
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name (optional)'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists
            if NewsletterSubscription.objects.filter(email=email, is_active=True).exists():
                raise ValidationError('This email is already subscribed to our newsletter.')
            return email.lower().strip()
        return email

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