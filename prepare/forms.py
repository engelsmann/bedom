# file: forms.py
# https://docs.djangoproject.com/en/3.2/topics/class-based-views/generic-editing/

from datetime import date, timedelta

#from django.db.models import fields
from django import forms
from django.core.exceptions import ValidationError
from django.forms import DateInput, ModelChoiceField
from django.http import request
#from django.http import HttpRequest, HttpResponse
from django.utils.dateparse import parse_datetime
from django.utils.timezone import datetime
from django.utils.translation import ugettext_lazy as _

import pytz

from .models import Forløb, Klasse, Modul # Forløb, 

class OpretModulForm(forms.ModelForm, object):
    klasse = ModelChoiceField(Klasse.objects)

    # Rækkefølge af felter: 
    # https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.field_order
    field_order = ['klasse','forløb','afholdt']
    # https://docs.djangoproject.com/en/3.2/ref/forms/widgets/#dateinput
    # https://stackoverflow.com/a/50243340/888033
        
#            'klasse': forms.Select(), # Unnecessary - default for Field type
    class Meta(object):
        model=Modul
        fields = ['klasse', 'forløb', 'afholdt'] 
        # https://docs.djangoproject.com/en/3.2/ref/forms/fields/#datefield
#        error_messages = {
#            'afholdt': { 
#                'invalid' : 
#                "Dato indtastes i formatet D/M/ÅÅÅÅ."
#            }
#        }

    # https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Forms#note_2
    # Skal kontrol på tværs af formular-felter holdes i Form.clean()? 
    # - JA: To niveauer - Først valideres UDEN KONTEXT (Findes forløbet?)
    # Med Forms.clean() kan niveau-1-validerede feltværdier valideres for sammenhæng.
    # Jeg prøvede at tilgå "fremmede clean_data" i clean_forløb (fx clean_data['klasse']),
    # og det fejler.
    # https://docs.djangoproject.com/en/3.2/ref/forms/validation/#validating-fields-with-clean
#    def clean_forløb(self):
#        data = self.cleaned_data['forløb']
#        return data

    def clean_afholdt(self):
        data = self.cleaned_data['afholdt']
        if data < date.today() + timedelta(weeks=1):
            raise ValidationError(
                _('Moduler kan højst oprettes med 1 uges tilbagevirkende kraft'),
                code='early'
            )
        if data > date.today() + timedelta(weeks=4): #datetime.
            raise ValidationError(
                _('Moduler kan højst oprettes 4 uger frem i tiden'),
                code='late'
            )
        return data

    def clean(self):
        cleaned_data = super().clean()
        klasse = cleaned_data.get('klasse')
        forløb = Forløb.objects.get(pk=cleaned_data.get('forløb').id)
        # Klasse-Forløb-relation kontrolleres
        if forløb.klasse != klasse:
            raise ValidationError( _('Forløb i korrekt klasse?'), code='non-related' )
        # Ligger Modul.afholdt -dato tidligst på og senest 3 måneder efter Forløb.påbegyndt -dato?
        afholdt = cleaned_data.get('afholdt') # None ???
        if afholdt == None:
            self.add_error(
                'afholdt',
                ValidationError(
                    _('Fucked-up dato!'),
                    code='afholdt=none'
                )
            )
        else:
            if afholdt < forløb.påbegyndt:
                self.add_error(
                    'afholdt',
                    ValidationError(
                        _('Moduler oprettes fra og med forløbsstart, ikke før.'),
                        code='early-f'
                    )
                ) 
            if forløb.påbegyndt + timedelta(weeks=13) < afholdt:
                self.add_error(
                    'afholdt',
                    ValidationError(
                       _('Moduler kan oprettes frem til 13 uger efter forløbsstart, ikke senere.'),
                        code='early-f'
                    )
                ) 
