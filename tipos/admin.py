from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(TipoDocumento)

admin.site.register(TipoObra)

admin.site.register(Documento)

admin.site.register(Categoria)