# file: forms.py
# https://docs.djangoproject.com/en/3.2/topics/class-based-views/generic-editing/

#from django.db.models import fields
from django import forms

from .models import Forløb, Klasse, Modul

class KlasseForm(forms.ModelForm):
    queryset = Klasse.objects.all()
    klasse = forms.ChoiceField(choices=queryset)
    class Meta:
        model=Klasse
        fields = ['kortnavn']

class ForløbForm(forms.ModelForm):
    klasse = forms.ChoiceField(choices=Klasse.objects.all())
    class Meta:
        model= Forløb
        fields=['klasse', 'emne', 'titel']

class ModulForm(forms.ModelForm):
    forløb = forms.ChoiceField(choices=Forløb.objects.all())
    class Meta:
        model=Modul
        fields=['forløb', 'afholdt']
