from django.contrib import admin

from .models import Exame, TipoEPI, EPI, CargoEPI, CargoExame, ASO, ExameRealizado

admin.site.register(Exame)
admin.site.register(TipoEPI)
admin.site.register(EPI)
admin.site.register(CargoEPI)
admin.site.register(CargoExame)
admin.site.register(ASO)
admin.site.register(ExameRealizado)