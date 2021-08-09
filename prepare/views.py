# File: prepare/views.py
from datetime import date

from django.db.models.lookups import BuiltinLookup
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import generic, View
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from .forms import OpretModulForm #ForløbForm #, KlasseForm klasse_form #, ModulForm ForløbForm,
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

# https://docs.djangoproject.com/en/3.2/ref/class-based-views/generic-display/#listview
class ElevListView(generic.ListView):
    model = Elev
    # https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Generic_views#note
    # Default template name: elev_list.html

class FokusGruppeUdvalgListView(generic.ListView):
    """
        Givet modul# (pk i URL) præsenteres brugeren for Elev-referencer: 
        Elever, der ikke endnu er blevet tildelt et modul, hvor læreren fokuserer på 
        netop DERES adfærd .
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
    model = FokusGruppe
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

class FokusGruppeView(generic.DetailView):
    model = FokusGruppe

# https://docs.djangoproject.com/en/3.2/ref/request-response/
class OpretModulFormView(View):
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