from django.contrib import admin
from django.forms import Textarea
from django.db import models

from .models import Ies, Carrera, Asignatura, Contenido, Homologacion, Analisis


# Register your models here.
class IesAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo')

class ContenidoInLine(admin.TabularInline):
    model = Contenido
    # classes = ('collapse', )
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':70})},
    }

class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel', 'codigo', 'carrera', 'horas')
    inlines = [ContenidoInLine,]

class AsignaturaInLine(admin.TabularInline):
    model = Asignatura
    extra = 0
    show_change_link = True
    
class CarreraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'modalidad', 'ies')
    inlines = [AsignaturaInLine,]

class AnalisisAdminInLine(admin.TabularInline):
    model = Analisis
    extra = 0

    class Meta:
        verbose_name = 'Analisis'
        verbose_name_plural = 'Analisis'

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        field = formset.form.base_fields["origen"]
        field.widget.can_add_related = False
        field.widget.can_change_related = False
        field.widget.can_delete_related = False
        field.widget.can_view_related = False
        field = formset.form.base_fields["destino"]
        field.widget.can_add_related = False
        field.widget.can_change_related = False
        field.widget.can_delete_related = False
        field.widget.can_view_related = False
        return formset
    
    def formfield_for_foreignkey(self,  db_field, request, **kwargs):
        try:
            h = Homologacion.objects.get(pk=request.resolver_match.kwargs.get('object_id')) 
            if db_field.name == 'origen':
                kwargs['queryset'] = Asignatura.objects.filter(carrera=h.origen) 
            if db_field.name == 'destino':
                kwargs['queryset'] = Asignatura.objects.filter(carrera=h.destino)
        except:
            pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class HomologacionAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'apellidos', 'nombres', 'fecha', 'origen', 'destino')
    inlines = [AnalisisAdminInLine,]

admin.site.register(Ies, IesAdmin)
admin.site.register(Carrera, CarreraAdmin)
admin.site.register(Asignatura, AsignaturaAdmin)
admin.site.register(Homologacion, HomologacionAdmin)