from django.urls import path
from . import views

urlpatterns = [
    path('', views.FokusGruppeListView.as_view(), name='index'),
    path('fokusgruppe_liste/',           views.FokusGruppeListView.as_view(), name='fokusgruppe_liste'),
    path('fokusgruppe_detalje_visning/', views.FokusGruppeView.as_view(),     name='fokusgruppe_detalje_visning'),
    path('elev_liste/',   views.ElevListView.as_view(), name='elev_liste'),    
    path('elev/<pk>', views.ElevView.as_view(),     name='elev_detaljer'),    
    path('fg_valg_klasse/', views.KlasseFormView.as_view(), name='fg_valg_klasse'),    
#   path('fg_valg_forloeb/<int:pk>/klasse', views.ForløbFormView.as_view(), name='fg_valg_forløb'),    
#    path('fg_valg_modul/<int:pk>/forloeb', views.KlasseFormView().as_view(), name='fg_valg_modul'),    
]
