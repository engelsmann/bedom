from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('elev_liste/', views.ElevListView.as_view(), name='elev_liste'),    
    path('elev/<pk>',   views.ElevView.as_view(),     name='elev_detaljer'),    
    path('opret_modul/',           views.OpretModulFormView.as_view(), name='opret_modul'),    
    path('modul_liste/',           views.ModulListView.as_view(), name='vælg_modul'),

    # Baglæns reference fra  prepare.models.modul.get_absolute_url
    path('modul_tildel/<int:pk>/', views.ProtoView.as_view(), name='modul_tildel'),
    path('~modul_tildel/<int:pk>/', views.FokusgruppeSelectFormView.as_view(), name='~modul_tildel'),
    path('~modul_tildel/<int:pk>/', views.FgTildelTilModulView.as_view(), name='~~modul_tildel'),
    path('~modul_tildel/<int:pk>/', views.FokusGruppeUdvalgListView.as_view(), name='~~~modul_tildel'),
    path('tildel/<int:pk>/modul', views.FokusGruppeUdvalgListView.as_view(), name='tildel'),    
    path('observationer/<int:pk>/modul', views.FokusGruppeObservationView.as_view(), name='observér'),    

#    path('fokusgruppe_liste/',           views.FokusGruppeListView.as_view(), name='fokusgruppe_liste'),
    path('fokusgruppe/<int:pk>', views.FokusGruppeView.as_view(),     name='fokusgruppe'),
]

## https://docs.djangoproject.com/en/3.2/topics/http/urls/#how-django-processes-a-request
## 4. Once one of the URL patterns matches, Django imports and calls the given view, 
# #   which is a Python function (or a class-based view). The view gets passed the following arguments:
##    - An instance of HttpRequest. 
#       # https://docs.djangoproject.com/en/3.2/ref/request-response/#django.http.HttpRequest
##    - If the matched URL pattern contained no named groups, then the matches from 
##      the regular expression are provided as positional arguments.
##    - The keyword arguments are made up of any named parts matched by the path expression 
##      that are provided, overridden by any arguments specified in 
##      the optional kwargs argument to django.urls.path() or django.urls.re_path().
