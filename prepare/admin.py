from django.contrib import admin

# Register your models here.
from .models import Adfærd, Elev, Emne, FokusGruppe, Forløb, Klasse, Modul, Skole, Video

admin.site.register(Skole)
admin.site.register(Klasse)
admin.site.register(Elev)
admin.site.register(Emne)
admin.site.register(Forløb)
admin.site.register(Modul)
admin.site.register(FokusGruppe)
admin.site.register(Adfærd)
admin.site.register(Video)
#admin.site.register()
