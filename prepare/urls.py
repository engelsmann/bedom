from django.urls import path
from . import views

urlpatterns = [
    path('', views.FokusGruppeListView.as_view(), name='index'),
    path('fokusgruppe_liste/', views.FokusGruppeListView.as_view(), name='fokusgruppe_liste'),
    path('fokusgruppe_detalje_visning/', views.FokusGruppeView.as_view(), name='fokusgruppe_detalje_visning'),
    
]
