from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('elev_liste/', views.ElevListView.as_view(), name='elev_liste'),    
    path('elev/<pk>',   views.ElevView.as_view(),     name='elev_detaljer'),    
    path('opret_modul/',           views.OpretModulFormView.as_view(), name='opret_modul'),    
    path('modul_liste/',           views.ModulListView.as_view(), name='vælg_modul'),

    # Baglæns reference fra  prepare.models.modul.get_absolute_url
    path('modul_tildel/<int:pk>/', views.FokusgruppeSelectFormView.as_view(), name='modul_tildel'),
#    path('modul_tildel/<int:pk>/', views.FgTildelTilModulView.as_view(), name='modul_tildel'),
#    path('modul_tildel/<int:pk>/', views.FokusGruppeUdvalgListView.as_view(), name='modul_tildel'),
#    path('tildel/<int:pk>/modul', views.FokusGruppeUdvalgListView.as_view(), name='tildel'),    
    path('observér/<int:pk>/modul', views.FokusGruppeObservationView.as_view(), name='observér'),    

#    path('fokusgruppe_liste/',           views.FokusGruppeListView.as_view(), name='fokusgruppe_liste'),
    path('fokusgruppe/<int:pk>', views.FokusGruppeView.as_view(),     name='fokusgruppe'),
]
