from django import forms
from .models import PotholeReport
from django.core.exceptions import ValidationError

class PotholeReportForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=15, required=False, label="Phone Number (optional)",
                                   widget = forms.TextInput(attrs = 
                                    {'placeholder': 'Enter your phone number', 'style': 'margin-right: 10 px'}))  # Optional phone number
    severity = forms.ChoiceField(
        choices = [(i, str(i)) for i in range(1, 6)], 
        widget = forms.RadioSelect, 
        label = "Severity of the Pothole"
    )  # Likert scale for severity
    latitude = forms.FloatField(widget = forms.HiddenInput())  # Latitude of the pothole location
    longitude = forms.FloatField(widget = forms.HiddenInput())  # Longitude of the pothole location
    image = forms.ImageField(required = True, label = "Upload Image", help_text = "Please only submit .jpg or .png files.")  # Image submission

    class Meta:
        model = PotholeReport
        fields = ['phone_number', 'severity', 'latitude', 'longitude', 'image']

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")

        if not latitude or not longitude:
            raise ValidationError("You must place a pin on the map to report the pothole.")

        return cleaned_data
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise ValidationError('Error: please submit a .jpg or .png file.')
        return image

class AuditReportForm(forms.Form):
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        label="Phone Number"
    )
    image = forms.ImageField(label="Upload an image of the covered pothole", help_text = "Please only submit .jpg or .png files.")

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise ValidationError('Error: please submit a .jpg or .png file.')
        return image