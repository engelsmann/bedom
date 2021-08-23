# file: forms.py
# https://docs.djangoproject.com/en/3.2/topics/class-based-views/generic-editing/

from datetime import date, timedelta

#from django.db.models import fields
from django import forms
from django.core.exceptions import ValidationError
from django.forms import DateInput, ModelChoiceField
from django.forms.fields import MultipleChoiceField

from django.http import request
from django.http import HttpRequest, HttpResponse
from django.utils.dateparse import parse_datetime
from django.utils.timezone import datetime
from django.utils.translation import ugettext_lazy as _

import pytz

from .models import Forløb, Klasse, Modul, FokusGruppe 

class ProtoForm(forms.ModelForm):
    class Meta:
        model = Modul
        fields = ['afholdt']
    def clean(self):
        # https://docs.djangoproject.com/en/3.2/ref/forms/validation/#validating-fields-with-clean
        return super().clean()

class FokusGruppeObserveForm(forms.ModelForm):
    class Meta:
        model=FokusGruppe
        fields = ['tilstede', 'spørg', 'hjælp', 'faglig', 'stikord']

class FokusgruppeSelectForm(forms.Form): # Ny version 11/8 2021
      # - Indskydelse (11/8, eftermiddag): Brug ModelForm, vølg kun afholdt og forløb felter.
      #   Formål: Form får "automatisk" PK-parameter. Elever vælges ud fra Klasse.
    # Brug PK parameter fra URLConf
    modul = Modul # Måske nok at definere class, giver View ikke PK? #.objects.get(modul=kwargs['pk'])
    select_ready_fg_members = FokusGruppe.objects\
        .filter(modul__isnull=True,elev__udmeldt__isnull=True).order_by('rand_rank')
    choices = [(q.id, q.elev.fornavn + ' ' + q.elev.efternavn) for q in select_ready_fg_members]       
    fokusgruppe = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=choices)

    def __init__(self, **kwargs):
        # Do I need to construct manually???
        # I think so, as I have a hard time putting the Modul identified by caller URL,
        # and I hope to access that Primary Key, PK, through Form self (or View self)?
        # OK, Didn't work as View constructor. Trying Form constructor
        super().__init__(**kwargs)
        
        ## Find Modul based on PK parameter (from UrlConf)
        ## Regarding HttpRequest.urlconf:
        ## https://docs.djangoproject.com/en/3.2/ref/request-response/#attributes-set-by-application-code
        # .urlconf ikke sat af middleware
        self.modul = Modul.objects.get(id=kwargs['pk']) # https://stackoverflow.com/a/41708655

        ## Locate Klasse object, etc in Modul
        forløb = self.modul.forløb
        self.klasse = forløb.klasse
        self.emne   = forløb.emne
        self.fag    = forløb.emne.fag

    def ensure_minimum_number_of_candidates(self):
        # If NOT ENOUGH len(choices)<10  (minimum = 10)
        # Copy Elev list (elev.klasse = modul.forløb.klasse) to FokusGruppe
        # recursively call to this method (which should pass in first recursion) or stop after two recursions
        # refresh select_ready_fg_members
        # refresh choices
        # refresh fokusgruppe
        pass


class OpretModulForm(forms.ModelForm, object):
    klasse = ModelChoiceField(Klasse.objects)

    # Rækkefølge af felter: 
    # https://docs.djangoproject.com/en/3.2/ref/forms/api/#django.forms.Form.field_order
    field_order = ['klasse','forløb','afholdt']
    # https://docs.djangoproject.com/en/3.2/ref/forms/widgets/#dateinput
    # https://stackoverflow.com/a/50243340/888033
        
    #'klasse': forms.Select(), # Unnecessary - default for Field type
    class Meta(object):
        model=Modul
        fields = ['klasse', 'forløb', 'afholdt'] 
        # https://docs.djangoproject.com/en/3.2/ref/forms/fields/#datefield
    #error_messages = {
    #        'afholdt': { 
    #            'invalid' : 
    #            "Dato indtastes i formatet D/M/ÅÅÅÅ."
    #        }
    #    }

    # https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Forms#note_2
    # Skal kontrol på tværs af formular-felter holdes i Form.clean()? 
    # - JA: To niveauer - Først valideres UDEN KONTEXT (Findes forløbet?)
    # Med Forms.clean() kan niveau-1-validerede feltværdier valideres for sammenhæng.
    # Jeg prøvede at tilgå "fremmede clean_data" i clean_forløb (fx clean_data['klasse']),
    # og det fejler.
    # https://docs.djangoproject.com/en/3.2/ref/forms/validation/#validating-fields-with-clean
    #def clean_forløb(self):
    #    data = self.cleaned_data['forløb']
    #    return data

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
