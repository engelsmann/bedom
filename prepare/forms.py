# file: forms.py
# https://docs.djangoproject.com/en/3.2/topics/class-based-views/generic-editing/

#from django.db.models import fields
from django import forms
from django.http import HttpRequest, HttpResponse
from .models import Forløb, Klasse, Modul

class KlasseForm(forms.ModelForm):
#def klasse_form(request):
    queryset = Klasse.objects.all()
    vælg_klasse = forms.ModelChoiceField(Klasse.objects)#choices=queryset)
    template_name = 'step1.html'
    class Meta:
        model=Klasse
        fields = ['kortnavn']
    def get(self, request, *args, **kwargs):
        context={
            'vælg_klasse' : self.vælg_klasse,
        }
        return render(request, 'step1', context=context)

    def post(self, request, *args, **kwargs):#    elif(request.method == 'POST'):
        context={}
        return render(request, 'step2.html', context=context)

#class ForløbForm(forms.ModelForm, klasse): forløb = forms.ModelChoiceField(choices=Forløb.objects.all(=klasse))  class Meta: model= Forløb  fields=['klasse', 'emne', 'titel']
#class ModulForm(forms.ModelForm): forløb = forms.ChoiceField(choices=Forløb.objects.all())  class Meta: model=Modul  fields=['forløb', 'afholdt']
