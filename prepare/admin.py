from django.contrib import admin

# Register your models here.
from .models import Skole, Klasse, Elev, Emne, Forløb, Modul, FokusGruppe, Adfærd

admin.site.register(Skole)
admin.site.register(Klasse)
admin.site.register(Elev)
admin.site.register(Emne)
admin.site.register(Forløb)
admin.site.register(Modul)
admin.site.register(FokusGruppe)
admin.site.register(Adfærd)
#admin.site.register()
