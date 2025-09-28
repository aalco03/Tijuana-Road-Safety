from django import forms
from .models import PotholeReport
from django.core.exceptions import ValidationError

class PotholeReportForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=15, required=False, label="Número de Teléfono (opcional)",
                                   widget = forms.TextInput(attrs = 
                                    {'placeholder': 'Introduzca su número de teléfono', 'style': 'margin-right: 10 px'}))  # Optional phone number
    severity = forms.ChoiceField(
        choices = [(i, str(i)) for i in range(1, 6)], 
        widget = forms.RadioSelect, 
        label = "Gravedad del Bache"
    )  # Likert scale for severity
    latitude = forms.FloatField(widget = forms.HiddenInput())  # Latitude of the pothole location
    longitude = forms.FloatField(widget = forms.HiddenInput())  # Longitude of the pothole location
    approximate_address = forms.CharField(max_length=255, required=False, widget=forms.HiddenInput())  # Address from geocoding
    image = forms.ImageField(required = True, label = "Subir Imagen", help_text = "Por favor, envíe únicamente archivos .jpg o .png.")  # Image submission

    class Meta:
        model = PotholeReport
        fields = ['phone_number', 'severity', 'latitude', 'longitude', 'approximate_address', 'image']

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")

        if not latitude or not longitude:
            raise ValidationError("Debes colocar un marcador en el mapa para reportar el bache.")

        return cleaned_data
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise ValidationError('Error: por favor, envíe únicamente archivos .jpg o .png.')
        return image

class AuditReportForm(forms.Form):
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        label="Número de Teléfono"
    )
    image = forms.ImageField(label="Suba una imagen del bache reparado")

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise ValidationError('Error: por favor, envíe únicamente archivos .jpg o .png.')
        return image