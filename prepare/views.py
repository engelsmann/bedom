# File: prepare/views.py
from datetime import date

from django.core.exceptions import ValidationError
from django.db.models.lookups import BuiltinLookup
from django import forms
from django.http      import HttpRequest, HttpResponse, HttpResponseRedirect, request, response
from django.shortcuts import render
from django.urls      import reverse
from django.utils.translation import gettext_lazy as _ # Or pgettext_lazy ?
from django.views                import generic, View
from django.views.generic.base   import TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit   import FormView
from django.views.generic.list   import ListView

from random import random # Kun brugt i tidligt udviklingstrin. Herefter bruges .models.FokusGruppe's egen Random.

from .forms import FokusgruppeSelectForm, FokusGruppeObserveForm, OpretModulForm, ProtoForm
from .models import Elev, Emne, FokusGruppe, Forløb, Klasse, Modul, Skole, Video

class HomeView(TemplateView):
    template_name='index.html'


class ElevView(generic.DetailView):
    """
        Elevens stamblad: 
        Vis klasse, studieretning, navn, (sammendrag af bedømmelser), (foto).
    """
    model = Elev
    context_object_name = 'elev_stamdata'
    template_name = 'prepare/elev_detaljer.html'


class ElevDashboard(generic.detail.SingleObjectMixin, generic.ListView):
    """
        Oversigt over alle præstationsbeskrivende ressourcer knyttet til en elev.
        https://docs.djangoproject.com/en/3.2/ref/class-based-views/mixins-simple/#django.views.generic.base.ContextMixin.extra_context
    """
    pass


class ElevListView(generic.ListView):
    # https://docs.djangoproject.com/en/3.2/ref/class-based-views/generic-display/#listview
    model = Elev
    # https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Generic_views#note
    # Default template name: elev_list.html

def protoview(request, **kwargs):
    """
        Aim: Handles URL pattern 'modul_tildel/<int:pk>/'
        Initial step: (GET) populates  Form.form  and list of  FokusGruppe.elev  instances 
                      RELATED TO  modul.forløb.klasse  BUT NOT YET related 
                      to  Modul  (as FokusGruppe.modul==Null).
        Receiving step: (POST) validates Modul.afholdt date
                        Validates the list POST.for_action as list of Boolean.
                        If valid:
                          Takes action (presents as changed, updates instance) on the following:
                          - If Modul.afholdt is changed.
                          - If for_action list is not empty.
                        If not valid:
                          Behaves as GET but with validation error messages.
    """
    modul = Modul.objects.get( id=kwargs['pk'] )
    if request.method == 'POST':
        form = ProtoForm(request.POST, instance=modul)
        if form.is_valid():
            # Date comparison?
            requested_module_date = form.cleaned_data['afholdt']
            #requested_module_date_type = type(requested_module_date)
            # https://docs.djangoproject.com/en/3.2/ref/models/instances/#refreshing-objects-from-database
            modul.refresh_from_db()
            afholdt_must_update = not (requested_module_date == modul.afholdt) 
            if afholdt_must_update:
                modul.afholdt = requested_module_date
                modul.save()
            # Only AFHOLDT validated by FORM
            # Primary Keys of FokusGruppe instances checked in list by user
            list_of_id_for_action = request.POST.getlist( 'for_action' )
            # Manually validate FOR_ACTION list
            clean = {}
            tmp = list()
            for i in list_of_id_for_action:
                #if type(i)=='str':
                tmp.append(int(i))
            if tmp: # len(tmp) != 0
                clean['fg_list_of_ids'] = tmp
                # QuerySet of instances to update
                fg_update_list = FokusGruppe.objects.filter(pk__in=tmp)
                # Update DB
                #modul.update(afholdt=clean['afholdt'])
                fg_update_list.update(modul=modul)

            context ={
                'modul' : modul,
                'afholdt_updates' : afholdt_must_update,
                'requested_module_date' : requested_module_date,
                #'requested_module_date_type' : requested_module_date_type
            }
            if 'fg_list_of_ids' in clean:
                context['fg_list_of_ids']= clean['fg_list_of_ids']
            if 'fg_update_list' in clean:
                context['fg_update_list'] = fg_update_list
            
            return render(request, 'confirm_changes.html', context)

    #else: 
    # POST not validated, or GET

    # Allerede tilmeldt
    tilmeldte_fg = FokusGruppe.objects.filter(
        modul=modul
    ).order_by('elev__fornavn') # https://stackoverflow.com/a/2065949/888033
    tilmeldt = [fg.elev for fg in tilmeldte_fg]

    # Relating Elev.klasse with Modul.forløb.klasse for Elev without Modul:
    roster_free = FokusGruppe.objects.filter(
        modul__isnull=True,
        elev__klasse=modul.forløb.klasse                
    ).order_by('rand_rank') # Gentaget nedenfor under betingelser
    roster_free_count = roster_free.count()
    roster_must_update = roster_free_count < modul.forløb.klasse.fokus_antal
    if roster_must_update:
        # Hent aktive elever i den klasse, som forløbet kører i:
        k_list = Klasse( modul.forløb.klasse.id ).elev_set.all()
        klasseliste = [(e, random()) for e in k_list]
        klasseliste = sorted(klasseliste, key=lambda x: x[-1]) # Sort list of tuples by last (-1) tuple element.
        klasseliste = [FokusGruppe(elev=e) for e,_ in klasseliste]
        for fg in klasseliste:
            fg.save()
        
        roster_free = FokusGruppe.objects.filter(
            modul__isnull=True,
            elev__klasse=modul.forløb.klasse                
        ).order_by('rand_rank')
    
    context = { 
        'modul' : modul,
        'form' : ProtoForm(instance=modul), # Errors when not validating POST?
        'fokusgruppe_liste' : roster_free,
        'tilmeldt' : tilmeldt,
        'antal_foreslået' : modul.forløb.klasse.fokus_antal - len(tilmeldt),
        'ryst_posen' : roster_must_update,
        'roster_free_count' : roster_free_count,
    }
    return render(request, 'proto.html', context)

class FokusgruppeSelectFormView(FormView):
    template_name = 'prepare/fokusgruppe_liste.html'
    form_class = FokusgruppeSelectForm #(kwargs)

    def __init__(self, *args, **kwargs):
        # Do I need to construct manually???
        # I think so, as I have a hard time putting the Modul identified by caller URL,
        # and I hope to access that Primary Key, PK, through Form self (or View self)?
        # OK, Didn't work as View constructor. Trying Form constructor
        # Trying to run the whole thing in get_context_data()
        #pass
        super(FormView, self).__init__(**kwargs)
        

    def my_fg_queryset(self):
        # (Kopieret fra FgTildelTilModulView)
        # https://docs.djangoproject.com/en/3.2/topics/db/queries/#field-lookups
        # https://docs.djangoproject.com/en/3.2/ref/models/querysets/#isnull
        self.klasse = Modul.objects.get(self.pk).forløb.klasse
        self.fg_queryset = FokusGruppe.objects.filter(modul__isnull=True).order_by('rand_rank')
        self.ikke_tildelt = self.fg_queryswt.count()

    def get_new_block(self):
        # (Kopieret fra FgTildelTilModulView)
        """
           Called by get_context_data().
           Takes Klasse related to the Modul and finds all Elev records related to Klasse.
           For each Elev: generate and store a FokusGruppe instance (with empty Modul reference).
           Then, the queryset is refreshed.
        """        
        ## Get all Elev objects related to Klasse object
        self.my_fg_queryset(self)
        #self.fg_queryst = FokusGruppe.objects.filter(elev__klasse=forløb.klasse).filter(modul__isnull=True)
        #self.ikke_tildelt = self.fg_queryst.count()
        
        if self.ikke_tildelt < self.paginate_by:

            ## For each Elev in Modul's Klasse: Generate FokusGruppe record 
            
            ## Refresh queryset - necessary ?
            self.my_set_queryset()
        else:
            ## Do nothing
            pass

    def get_context_data(self, **kwargs):
        # (Kopieret fra FgTildelTilModulView)
        # https://stackoverflow.com/q/46168117/888033
        context = super(FokusgruppeSelectFormView, self).get_context_data(**kwargs) # KWARGS ukendt
        ## Find Modul based on PK parameter (from UrlConf)
        self.modul = Modul.objects.get(id=request.pk) # https://stackoverflow.com/a/41708655

        ## Locate Klasse object, etc in Modul
        forløb = self.modul.forløb
        self.klasse = forløb.klasse
        self.emne   = forløb.emne
        self.fag    = forløb.emne.fag

        context = {
            'modul' : self.modul, # Giver Klasse = modul.klasse, Emne = modul.forløb.emne, Fag = modul.forløb.emne.fag
            # List of 2-tuples to MultipleChoiceField
            # https://docs.djangoproject.com/en/3.2/ref/forms/fields/#multiplechoicefield
            # itemgetter? https://stackoverflow.com/a/39702851/888033
            'navneliste_checkboxe'  : self.navneliste_checkboxe,
            'ikke_tildelt' : self.ikke_tildelt,
            'klasse' : self.klasse,
            'emne' : self.emne,
            'fag' : self.fag
        } 
        return context

    def get_success_url(self):
        """
            Når modul (PK) har fået sine kandidater, præsenteres modulet MED LISTE over disse kandidater
            https://docs.djangoproject.com/en/3.2/ref/class-based-views/mixins-editing/#django.views.generic.edit.FormMixin.get_success_url
        """
        # https://docs.djangoproject.com/en/3.2/ref/urlresolvers/#reverse
        return reverse(
            "fokusgruppe_klar", 
            kwargs = {
                'pk' : self.pk ## Mon ikke View-objektet 'self' har PARAMETEREN 'pk', den er kaldt med, fra UrlConf?
            }
        )

    def form_valid(self, form):
        """
            Called on POST when FORM data validate.
            Redirects to get_success_url().
            https://docs.djangoproject.com/en/3.2/ref/class-based-views/mixins-editing/#django.views.generic.edit.FormMixin.form_valid
        """
        form.ensure_minimum_number_of_candidates() #
        return super().form_valid(form)


class FgTildelTilModulView(View):
    """
    Omstrukturering af FokusGruppeUdvalgListView:
    - Modul PK
    GET
    - Alle FokusGruppe med tomt .modul felt sorteret efter .rand_rank felt.
    - Context: 
      - Modul: for at gøre skemabrik / Modul forståeligt for læreren (dato, klasse, fag, emne))
      - nogle FokusGruppe - objekter: Elev-navne, der knyttes sammen som fokusgruppe i dette modul.
    POST
    - Opdater FokusGruppe-objekter med CHECKED box mht. .modul felt.
    - Redirect til static HTML side: "tildeling ok" = "succes".
    """
    template_name = 'prepare/fokusgruppe_liste.html'
    paginate_by = 10

    def my_set_queryset(self):
        # https://docs.djangoproject.com/en/3.2/topics/db/queries/#field-lookups
        # https://docs.djangoproject.com/en/3.2/ref/models/querysets/#isnull  
        self.queryset = FokusGruppe.objects.filter(modul__isnull=True).order_by('rand_rank')
        self.ikke_tildelt = self.queryset.count()

    def get_new_block(self, pk):
        """
           Called by get_context_data().
           Takes Klasse related to the Modul and finds all Elev records related to Klasse.
           For each Elev: generate and store a FokusGruppe instance (with empty Modul reference).
           Then, the queryset is refreshed.
        """        
        ## Find modul
        self.modul = Modul.objects.get(id=pk) # https://stackoverflow.com/a/41708655

        self.modul.afholdt

        # self.my_set_queryset() ## Operationer lagt herunder i stedet for i særskilt metode (?)

        ## Locate Klasse, etc in Modul
        forløb      = self.modul.forløb
        self.klasse = forløb.klasse
        self.emne   = forløb.emne
        self.fag    = forløb.emne.fag

        ## Get all Elev related to Klasse instance
        klasse_størrelse = Elev.objects.filter().count() # For DEBUG only
        self.queryset = FokusGruppe.objects.filter(elev__klasse=forløb.klasse).filter(modul__isnull=True)
        self.ikke_tildelt = self.queryset.count()
        
        if self.ikke_tildelt < self.paginate_by:

            ## For each Elev: Generate FokusGruppe record 
            
            ## Refresh queryset
            self.my_set_queryset()
        else:
            ## Do nothing
            pass

    def get_context_data(self):
        #context = super(FgTildelTilModulView).get_context_data(**kwargs)
        context = {
            'modul' : self.modul, # Giver Klasse = modul.klasse, Emne = modul.forløb.emne, Fag = modul.forløb.emne.fag
            # List of 2-tuples to MultipleChoiceField
            # https://docs.djangoproject.com/en/3.2/ref/forms/fields/#multiplechoicefield
            # itemgetter? https://stackoverflow.com/a/39702851/888033
            'navneliste_checkboxe'  : self.navneliste_checkboxe,
            'ikke_tildelt' : self.ikke_tildelt,
            'klasse' : self.klasse,
            'emne' : self.emne,
            'fag' : self.fag
        } 
        return context

    def get(self, request, pk):
        self.get_new_block(pk)
        choices = [(q.id, q.elev.fornavn + ' ' + q.elev.efternavn) for q in self.queryset]       
        f = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=choices)
        self.navneliste_checkboxe = choices
        return render(request, self.template_name, self.get_context_data())
        

    def post(self, request, *args, **kwargs):
        modul = Modul.objects.get(pk=self.kwargs['modul']) # Som i GET()


class FokusGruppeUdvalgListView(View):
    """
        Givet modul# (pk i URL) præsenteres brugeren for Elev-referencer: 
        Elever, der ikke endnu er blevet tildelt et modul, hvor læreren fokuserer på 
        netop DERES adfærd, kan vinges af i checkbokse i dette view (template), og deltager dermed
        i den FokusGruppe, der er tilknyttet modulet.
            (1) Hvis der er *tilstrækkeligt* med objekter hvor `modul=Null`, dvs. at den
                pågældende elev endnu ikke er tilknyttet et modul som medlem af en fokusgruppe:
                - Vis (pagineret) med de første `klasse.fokus_antal` sorterede elever 
                  foreslået som `<input ... CHECKED>`. Altså dem med lavest `rand_rank`.
                - Brugeren udvælger (antal) medlemmer af modulets fokusgruppe 
                  på listen med disse objekter og indsender formularen.
            (2) Hvis antallet er utilstrækkeligt, GENERERES et nyt "klassesæt", 
                som sorteres efter `rand_rank` og gemmes i databasen.
                Herefter tages trin (1).
            (3) Når modulets fokusgruppe er registreret, valideres det indsendte. 
                Der skal være:
                - Mindst 2 medlemmer, modul-checkbox `checked`;
                - Højst `paginate_by` (10) medlemmer, modul-checkbox `checked`;
            (4) Rækken for hver af de indsendte "kandidater" opdateres. 
            (5) Brugeren sendes til applikationens forside.
        Trin 1 og 2 bor i GET-forespørgslen, trin 3-5 sker som respons på POST-forespørgslen.
    """
    model = Modul
    paginate_by = 10
    context_object_name = 'fokusgruppe_liste' # Your own name for the list as a template variable
    template_name = 'prepare/fokusgruppe_liste.html'  # Template name: fokusgrupper / filename: fokusgruppe-liste.html

    def my_set_queryset(self):
        # https://docs.djangoproject.com/en/3.2/topics/db/queries/#field-lookups
        # https://docs.djangoproject.com/en/3.2/ref/models/querysets/#isnull  
        self.queryset = FokusGruppe.objects.filter(modul__isnull=True).order_by('rand_rank')
        self.ikke_tildelt = self.queryset.count()

    def get_new_block(self):
        """
           Called by get_context_data().
           Takes Klasse related to the Modul and finds all Elev records related to Klasse.
           For each Elev: generate and store a FokusGruppe instance (with empty Modul reference).
           Then, the queryset is refreshed.
        """
        self.my_set_queryset()

        if self.ikke_tildelt < self.paginate_by:
            # Find modul

            # Locate Klasse in Modul

            # Get all Elev related to Klasse instance

            # For each Elev: Generate FokusGruppe record 
            
            # Refresh queryset
            self.my_set_queryset()
        else:
            # Do nothing
            pass

    #    def get_query_set(self):
    #       return Modul.objects.filter()
    def get_context_data(self, **kwargs):
        """
            ENTEN overskriv get_context_data() ELLER definer get_query_set()
            https://stackoverflow.com/q/51631651/888033
            https://docs.djangoproject.com/en/3.2/ref/class-based-views/mixins-simple/#django.views.generic.base.ContextMixin.get_context_data
            You can also use the extra_context attribute.
            https://docs.djangoproject.com/en/3.2/ref/class-based-views/mixins-simple/#django.views.generic.base.ContextMixin.extra_context
        """
        self.get_new_block()
        # Call the base implementation first to get the context
        context = super(FokusGruppeUdvalgListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        #context['nr1'] = self.queryset.all()[0].elev_fg_runde_id
        # Antal elever i FokusGruppe, som er (ikke er) tildelt et observationsmodul
        context['antal_ikke_tildelt'] = self.ikke_tildelt
        context['idag'] = self.idag
        context['modul_dato'] = self.idag
        return context

    # https://stackoverflow.com/a/3798865/888033
    @property
    def idag(self):
        return True #date.today() == self.model.modul.afholdt

# Blev gjort opmærksom på, at HTTP 405 med DetailView skyldtes design:
# Ændringer / POST kræver UpdateView: https://stackoverflow.com/a/39993806/888033
class FokusGruppeView(generic.UpdateView):
    model = FokusGruppe
    form=FokusGruppeObserveForm
    fields = ['tilstede', 'spørg', 'hjælp', 'faglig', 'stikord']
    template_name = 'prepare/fokusgruppe_detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context["form"] = self.form
        return context
    
    def clean(self):
        """
            Raises ValidationError, if "tilstede" is True WITHOUT all three of "spørg", "hjælp" and "faglig"
            being set (not Null).
            https://docs.djangoproject.com/en/3.2/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
            https://docs.djangoproject.com/en/3.2/ref/forms/validation/#raising-validation-error
        """
        cleaned_data = super().clean()
        tilstede = cleaned_data.get("tilstede")
        spørg    = cleaned_data.get("spørg")
        hjælp    = cleaned_data.get("hjælp")
        faglig   = cleaned_data.get("faglig")
        stikord  = cleaned_data.get("stikord")
        if tilstede == True:
            if spørg and hjælp and faglig:
                pass # Everything is good and fine!
            else:
                self.add_error( ValidationError(
                    _('Når eleven er registreret som tilstede i modulet %(tilstede)s, kræves Spørgefærdighed udfyldt %(spørg)i, relevans af ydet hjælp %(hjælp)i, niveau af faglig samtale %(faglig)i. Også lærerens stikord kan kun bedømmes "%(stikord)s" er medtaget her.'), 
                    code='inconsistent',
                    params = {
                        'tilstede' : tilstede,
                        'spørg' : spørg,
                        'hjælp' : hjælp,
                        'faglig' : faglig,
                        'stikord' : stikord
                    }
                ))
        else: # tilstede False or None
            if tilstede is not None and spørg and hjælp and faglig and stikord:
                self.add_error( ValidationError(
                    _('Spørgefærdighed %(spørg)i, relevans af ydet hjælp %(hjælp)i, niveau af faglig samtale %(faglig)i samt lærerens stikord "%(stikord)s" kan kun bedømmes, hvis eleven er registreret som tilstede i modulet: %(tilstede)s.'), 
                    code='inconsistent',
                    params = {
                        'tilstede' : tilstede,
                        'spørg' : spørg,
                        'hjælp' : hjælp,
                        'faglig' : faglig,
                        'stikord' : stikord
                    }
                ))
        
    


class OpretModulFormView(View):
    # https://docs.djangoproject.com/en/3.2/ref/request-response/
    """
        For læreren til at oprette Modul.
        Redirect, når modulet er oprettet, til URL 'modulets_fokusgruppe/'
    """
    # https://docs.djangoproject.com/en/3.2/ref/forms/fields/#fields-which-handle-relationships
    form_class = OpretModulForm
    template_name = 'prepare/modul_opret.html'

    def get(self, request, *args, **kwargs):
        return render(
            request, 
            self.template_name, 
            {
                # https://docs.djangoproject.com/en/3.2/ref/forms/api/#as-p
                # Repræsentationsformen AS_P er placeret i Template, se dette
                'form':         self.form_class, 
            }
        ) 

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            # Opret eller hent Modul objekt
            modul, created = Modul.objects.get_or_create(
                forløb = form.cleaned_data['forløb'],
                afholdt = form.cleaned_data['afholdt'],
            )
            #if( created ):
            # Opdatér nyoprettet modul objekt
            modul.save()

            # Process form cleaned data by presenting the next step in Modul selection flow
            # Field `id` in Forløb instance selected by user and POSTed back to server
            return HttpResponseRedirect('/fg_valg/{}/modul/'.format(modul.id))
            #else:
                # Modul er ikke nyt, oprettes derfor ikke
            #    pass
        
        # Brugeren får sin forkert udfyldte FORM tilbage
        return render(
            request, 
            self.template_name, 
            {'form': form} #_class}
        )


class ModulListView(generic.ListView):
    """
        Præsentere liste med links til moduler.
    """
    model=Modul
    template_name = "prepare/modul_vælg.html"

    #    class Meta:
    #        pass

    def get_context_data(self, **kwargs):
        context = super(ModulListView, self).get_context_data(**kwargs)
        context["idag"] = self.idag
        return context

    # https://stackoverflow.com/a/3798865/888033
    @property
    def idag(self):
        return date.today() == self.model.afholdt


class FokusGruppeObservationView(generic.DetailView):
    pass