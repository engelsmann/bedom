from django.shortcuts import render
from django.views import generic

from .models import Adfærd, Elev, Emne, FokusGruppe, Forløb, Klasse, Modul, Skole, Video


# https://docs.djangoproject.com/en/3.2/ref/class-based-views/generic-display/#listview
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