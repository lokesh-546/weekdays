from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
import re
import os
from django.core.exceptions import ValidationError
ROLE_CHOICES = [
    ('', 'Select Role'),
    ('PROFESSIONAL', 'Construction Professional'),
    ('OWNER', 'Owner'),
    ('MARKETER', 'Real Estate Agent'),
]

 

CATEGORY_CHOICES = [
    ('Plumber', 'Plumber'),
    ('Painter', 'Painter'),
    ('Electrician', 'Electrician'),
    ('Constructor', 'Constructor'),
    ('Centring', 'Centring'),
    ('Interior designer', 'Interior designer'),
    ('Architecture', 'Architecture'),
    ('Civil engineer', 'Civil engineer'),
    ('Tiles works', 'Tiles works'),
    ('Marble works', 'Marble works'),
    ('Granite works', 'Granite works'),
    ('Wood works', 'Wood works'),
    ('Glass works', 'Glass works'),
    ('Steel railing works', 'Steel railing works'),
    ('Carpenter', 'Carpenter'),
    ('Doozer works', 'Doozer works'),
    ('JCB works', 'JCB works'),
    ('Borewells', 'Borewells'),
    ('Material supplier', 'Material supplier'),
]

MARKETER_CATEGORIES = [
    ('Plot', 'Plot'),
    ('House', 'House'),
    ('Flat', 'Flat'),
    ('Villa', 'Villa'),
    ('Farm', 'Farm'),
    ('Lands', 'Lands'),
    ('Developmentlands', 'Developmentlands'),
]

PLAN_CHOICES = [
    ('MARKETER_EXPORT', 'Experts'),
    ('MARKETER_EXPORT_PRO', 'Experts Pro'),
    ('MARKETER_EXPORT_PREMIUM', 'Expert Premium'),
]


class UserRegisterForm(UserCreationForm):

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False
    )

    marketer_category = forms.MultipleChoiceField(
        choices=MARKETER_CATEGORIES,
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'marketer-checkboxes'}
        )
    )

    plan_type = forms.ChoiceField(
        choices=PLAN_CHOICES,
        required=False,
        widget=forms.RadioSelect(attrs={'class': 'plan-radio-select'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username', 'email', 'phone',
            'role',
            'category',
            'marketer_category',
            'plan_type',
            'profile_image_path',
            'referred_by_code',
        )

    # ✅ THIS MUST BE INSIDE CLASS
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        role_selected = None

        if self.data.get('role'):
            role_selected = self.data.get('role')
        elif self.instance and self.instance.role:
            role_selected = self.instance.role

        # PROFESSIONAL + OWNER
        if role_selected in ['PROFESSIONAL', 'OWNER']:
            self.fields['category'].choices = CATEGORY_CHOICES

        # MARKETER
        if role_selected == 'MARKETER':
            self.fields['marketer_category'].choices = MARKETER_CATEGORIES

        # Edit mode support
        if self.instance.pk and self.instance.marketer_category:
            self.initial['marketer_category'] = self.instance.marketer_category.split(',')

    def clean_username(self):
        username = self.cleaned_data.get("username")
        username = " ".join(username.split())
        return username

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        plan_type = cleaned_data.get("plan_type")

        if role == "MARKETER" and not plan_type:
            self.add_error(
                "plan_type",
                "Choose Experts / Experts Pro / Experts Premium"
            )

        return cleaned_data
 

from django import forms
from .models import AddPropertyModel
import re
import json


class AddPropertyForm(forms.ModelForm):

    # =========================
    # CHOICES
    # =========================
    AMENITY_CHOICES = [
        ('Swimming Pool', 'Swimming Pool'),
        ('Gym', 'Gym'),
        ('Playground', 'Playground'),
        ('Park', 'Park'),
        ('Club House', 'Club House'),
    ]

    FURNITURE_CHOICES = [
        ('Furnished', 'Furnished'),
        ('Semi-Furnished', 'Semi-Furnished'),
        ('Unfurnished', 'Unfurnished'),
    ]

    RERA_CHOICES = [
        ("True", "Yes"),
        ("False", "No"),
    ]

    # =========================
    # RERA
    # =========================
    reraApproved = forms.ChoiceField(
        choices=RERA_CHOICES,
        widget=forms.RadioSelect,
        label="RERA Approved"
    )

    # =========================
    # FURNITURE
    # =========================
    furniture = forms.ChoiceField(
        choices=FURNITURE_CHOICES,
        required=False,
        label="Furniture Type",
        widget=forms.RadioSelect
    )

    # =========================
    # AMENITIES
    # =========================
    predefined_amenities = forms.MultipleChoiceField(
        choices=AMENITY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select Amenities"
    )

    custom_amenities_text = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Add other amenity (comma-separated)'
        }),
        label="Other Amenities"
    )

    # =========================
    # NEARBY PLACES (NEW UI)
    # =========================
    nearby_places_text = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = AddPropertyModel
        fields = [
            'look', 'selectProperty', 'projectName', 'extent', 'facing', 'roadSize',
            'units', 'dimensions', 'numberOfFloors', 'numberOfBHK', 'builtUpArea',
            'openArea', 'rentalIncome', 'floorNo', 'communityType', 'carpetArea',
            'landType', 'soilType', 'roadFacing', 'waterSource', 'unitType', 'zone',
            'developmentType', 'expectedAdvance', 'ratio', 'disputeDetails',
            'lookingToSell', 'problemDetails', 'actualPrice', 'salePrice', 'price',
            'reraApproved', 'approvalType', 'highlights', 'address', 'locationUrl',
            'image', 'video', 'document', 'image1', 'image2', 'image3', 'image4',
            'furniture', 'deposit',
        ]

    # =========================
    # CLEAN RERA
    # =========================
    def clean_reraApproved(self):
        value = self.cleaned_data.get("reraApproved")
        return True if value == "True" else False

    # =========================
    # INIT
    # =========================
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['look'].choices = AddPropertyModel.LOOKING_CHOICES
        self.fields['selectProperty'].choices = AddPropertyModel.PROPERTY_CHOICES

        # Auto format labels
        for field_name, field in self.fields.items():
            label = re.sub(r'([a-z])([A-Z])', r'\1 \2', field_name)
            label = label.replace('_', ' ')
            field.label = label.title()

        # =========================
        # AMENITIES (EDIT MODE)
        # =========================
        if self.instance and self.instance.pk and self.instance.amenities:
            selected_predefined = []
            custom_amenities_list = []

            for amenity in self.instance.amenities:
                if amenity in dict(self.AMENITY_CHOICES):
                    selected_predefined.append(amenity)
                else:
                    custom_amenities_list.append(amenity)

            self.initial['predefined_amenities'] = selected_predefined
            self.initial['custom_amenities_text'] = ", ".join(custom_amenities_list)

        # =========================
        # NEARBY PLACES (EDIT MODE)
        # =========================
        if self.instance and self.instance.pk and self.instance.nearby_places:
            try:
                self.initial['nearby_places_text'] = json.dumps(self.instance.nearby_places)
            except:
                self.initial['nearby_places_text'] = "[]"

        # =========================
        # PLACEHOLDERS
        # =========================
        placeholders = {
            'projectName': 'Ex: Green Valley Apartments',
            'extent': 'Enter plot area in sq. yards',
            'facing': 'Ex: North, South',
            'roadSize': 'Ex: 30 ft',
            'units': 'Number of units',
            'dimensions': 'Length × Width',
            'numberOfFloors': 'Ex: 2',
            'numberOfBHK': 'Ex: 3',
            'builtUpArea': 'In sq. ft.',
            'openArea': 'In sq. ft.',
            'rentalIncome': 'Monthly rental income',
            'floorNo': 'Floor number',
            'communityType': 'Ex: Gated Community',
            'carpetArea': 'In sq. ft.',
            'landType': 'Ex: Agriculture',
            'soilType': 'Ex: Clay, Sandy',
            'roadFacing': 'Check if road facing',
            'waterSource': 'Ex: Borewell, Municipal',
            'unitType': 'Ex: Studio, 2BHK',
            'zone': 'Ex: Zone A',
            'developmentType': 'Ex: Plot, Villa',
            'expectedAdvance': 'Advance amount expected',
            'ratio': 'Ex: 70:30',
            'disputeDetails': 'Any disputes details',
            'lookingToSell': 'Check if property is for selling',
            'problemDetails': 'Problems with property if any',
            'actualPrice': 'Actual property price',
            'salePrice': 'Selling price',
            'price': 'Current price',
            'approvalType': 'Ex: HMDA / DTCP',
            'highlights': 'Highlight property features',
            'address': 'Full property address',
            'locationUrl': 'Google Maps URL',
            'deposit': 'Security deposit (if any)',
        }

        for field_name, placeholder_text in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['placeholder'] = placeholder_text

    # =========================
    # SAVE METHOD
    # =========================
    def save(self, user, commit=True):
        instance = super().save(commit=False)
        instance.user = user

        # =========================
        # AMENITIES SAVE
        # =========================
        all_amenities = []

        if self.cleaned_data.get('predefined_amenities'):
            all_amenities.extend(self.cleaned_data['predefined_amenities'])

        if self.cleaned_data.get('custom_amenities_text'):
            custom_list = [
                a.strip()
                for a in self.cleaned_data['custom_amenities_text'].split(',')
                if a.strip()
            ]
            all_amenities.extend(custom_list)

        instance.amenities = all_amenities

        # =========================
        # NEARBY PLACES SAVE
        # =========================
        nearby_data = self.cleaned_data.get('nearby_places_text')

        if nearby_data:
            try:
                instance.nearby_places = json.loads(nearby_data)
            except:
                instance.nearby_places = []
        else:
            instance.nearby_places = []

        if commit:
            instance.save()

        return instance
# my requremt form

class FutureRequirementForm(forms.ModelForm):
    class Meta:
        model = FutureRequirement
        fields = '__all__'



from django import forms
from .models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'phone',
            'category',
            'location',
            'deals',
            'experience',
            'description',
            'profile_image_path'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

from django import forms
from .models import MoveRequest

class MoveRequestForm(forms.ModelForm):
    class Meta:
        model = MoveRequest
        fields = '__all__'

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

COMPANY_CATEGORIES = [
    ('Open Flat', 'Open Flat'),
    ('Villa', 'Villa'),
    ('Apartment', 'Apartment'),
    ('Farm Flats', 'Farm Flats'),
    ('Commercial Lands', 'Commercial Lands'),
]

PLAN_CHOICES = [
    ('NORMAL', 'Normal'),
    ('PRO', 'Pro'),
    ('PREMIUM', 'Premium'),
]

class CompanyRegisterForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(required=True, widget=forms.Textarea)
    experience = forms.IntegerField(required=True, min_value=0)
    total_projects = forms.IntegerField(required=True, min_value=0)
    ongoing_projects = forms.IntegerField(required=True, min_value=0)
    completed_projects = forms.IntegerField(required=True, min_value=0)
    address = forms.CharField(max_length=255, required=True)
    phone = forms.CharField(max_length=15, required=True)
    location = forms.CharField(required=True)
    company_wallpaper_path = forms.ImageField(required=True)
    company_logo_path = forms.ImageField(required=True)

    # ✅ Changed to MultipleChoiceField (checkbox support)
    category = forms.MultipleChoiceField(
        choices=COMPANY_CATEGORIES,
        required=True,
        widget=forms.CheckboxSelectMultiple
    )

    # ✅ Match your template plan values
    plan = forms.ChoiceField(
        choices=PLAN_CHOICES,
        required=True,
        widget=forms.HiddenInput()
    )

    # ✅ Duration added (if using hidden field in HTML)
    duration = forms.IntegerField(required=True)

    class Meta:
        model = User
        fields = [
            "username", "email", "password1", "password2",
            "company_name", "description", "experience",
            "total_projects", "ongoing_projects", "completed_projects",
            "address", "phone",
            "company_wallpaper_path", "company_logo_path", "location",
            "category", "plan", "duration"
        ]

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)

        # ✅ Convert category list to string (if model has CharField)
        user.category = ", ".join(self.cleaned_data["category"])

        if commit:
            user.save()

        return user
class FranchiseForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    location = forms.CharField(max_length=255, required=True)
    radius = forms.IntegerField(required=False, initial=5, widget=forms.HiddenInput())
    description = forms.CharField(widget=forms.Textarea, required=True)
    experience = forms.IntegerField(required=True)
    profile_image = forms.ImageField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone",
            "location",
            "radius",
            "description",
            "experience",
            "profile_image",
            "password1",
            "password2",
        ]

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone
    def save(self, commit=True):
        user = super().save(commit=False)
        user.radius = 5   
        if commit:
            user.save()
        return user
    
class ReelsForm(forms.ModelForm):
  class Meta:
        model=Reels
        fields=['reel','description','link']



from .models import FranchiseApplication

class FranchiseApplicationForm(forms.ModelForm):
    class Meta:
        model = FranchiseApplication
        fields = ['full_name', 'email', 'contact', 'location', 'experience', 'reason']
        widgets = {
            'experience': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Describe your experience'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Why do you want to start a franchise?'}),
            'contact': forms.TextInput(attrs={'placeholder': 'Enter contact number'}),
        }

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        if not contact.isdigit():
            raise forms.ValidationError("Contact must be numeric.")
        return contact
        




from django import forms
from .models import ChatMessage


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Type your message...',
                'class': 'form-control'
            })
        }


from .models import PostFeed, ImagePost

class PostFeedForm(forms.ModelForm):
    class Meta:
        model = PostFeed
        fields = '__all__'


class ImagePostForm(forms.ModelForm):
    class Meta:
        model = ImagePost
        fields = ['news_content', 'image', 'video']



class NewsPostForm(forms.ModelForm):
    heading = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    news_content = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))

    class Meta:
        model = NewsPost
        fields = ['heading', 'news_content']
