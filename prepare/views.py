from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import generic, View

from .forms import KlasseForm, ForløbForm, ModulForm
from .models import Elev, Emne, FokusGruppe, Forløb, Klasse, Modul, Skole, Video

class ElevView(generic.DetailView):
    """
        Elevens stamblad: 
        Vis klasse, studieretning, navn, (sammendrag af bedømmelser), (foto).
    """
    model = Elev
    context_object_name = 'elev_stamdata'
    template_name = 'prepare/elev_detaljer.html'

# https://docs.djangoproject.com/en/3.2/ref/class-based-views/generic-display/#listview
class ElevListView(generic.ListView):
    model = Elev
    # https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Generic_views#note
    # Default template name: elev_list.html

class FokusGruppeListView(generic.ListView):
    model = FokusGruppe
    paginate_by = 10
    context_object_name = 'fokusgruppe_liste'   # your own name for the list as a template variable
    queryset = FokusGruppe.objects.all()
    #queryset = FokusGruppe.objects.filter(klasse__icontains='1')[:5] # Get 5 FokusGrupper containing the Klasse "1"
    template_name = 'fokusgruppe_liste.html'  # Template name: fokusgrupper / filename: fokusgruppe-liste.html


    def get_context_data(self, **kwargs):
        """Modifikationer af nedarvet metode"""
        # Call the base implementation first to get the context
        context = super(FokusGruppeListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['nr1'] = self.queryset.all()[0].elev_fg_runde_id
        # Antal elever i FokusGruppe, som er (ikke er) tildelt et observationsmodul
        context['tildelt']       = self.queryset.filter(modul__isnull=False)
        context['antal_tildelt'] = self.queryset.filter(modul__isnull=False).count()
        context['ikke_tildelt']       = self.queryset.filter(modul__isnull=True)
        context['antal_ikke_tildelt'] = self.queryset.filter(modul__isnull=True).count()
        return context

class FokusGruppeView(generic.DetailView):
    model = FokusGruppe
    context_object_name = 'fokusgruppe_detalje_visning'

# https://docs.djangoproject.com/en/3.2/ref/request-response/
class KlasseFormView(View):
    """
        View til at vælge klasse, når læreren skal vælge modul (trin 1)
    """
    def get(self, request, *args, **kwargs):
        form = self.form_class()#initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # Process form cleaned data by presenting the next step in Modul selection flow
            # Field `id` in Klasse instance selected by user and POSTed back to server
            return HttpResponseRedirect('/fg_valg_forloeb/{}/klasse/'.format(form.klasse.id))

        return render(request, self.template_name, {'form': form})

# https://docs.djangoproject.com/en/3.2/ref/class-based-views/base/#templateview
class VælgForløbView(generic.base.TemplateView):
    template_name = "vælg_forløb.html"

    def get_context_data(self, id, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forløbsliste'] = Forløb.objects.get_klasse(pk=id)
        return context