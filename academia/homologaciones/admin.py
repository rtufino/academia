import io 
import xlsxwriter

from django.contrib import admin
from django.forms import Textarea
from django.db import models
from django.http import HttpResponse

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
    fields = ('nivel', 'nombre', 'horas')
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

    def exportar(self, request, queryset):
        output = io.BytesIO()

        # Even though the final file will be in memory the module uses temp
        # files during assembly for efficiency. To avoid this on servers that
        # don't allow temp files, for example the Google APP Engine, set the
        # 'in_memory' Workbook() constructor option as shown in the docs.
        workbook = xlsxwriter.Workbook(output)

        for registro in queryset:
            row = 0
            col = 0

            worksheet = workbook.add_worksheet(name=registro.cedula)
            
            worksheet.write(row, col, 'CÓDIGO')
            worksheet.write(row, col+1, 'NOMBRE')
            worksheet.write(row, col+2, 'NIVEL')
            worksheet.write(row, col+3, 'CÓDIGO')
            worksheet.write(row, col+4, 'NOMBRE')
            worksheet.write(row, col+5, 'CALIFICACIÓN CON LA QUE APRUEBA LA ASIGNATURA')
            worksheet.write(row, col+6, 'CALIFICACIÓN TOTAL DE APROBACIÓN DE LA IES ORIGEN')
            worksheet.write(row, col+7, 'NÚMERO DE HORAS / CRÉDITOS')
            worksheet.write(row, col+8, 'FECHA / PERÍODO ACADÉMICO DE APROBACIÓN')
            worksheet.write(row, col+9, 'PORCENTAJE DE CORRESPONDENCIA HORAS')
            worksheet.write(row, col+10, 'PORCENTAJE DE CORRESPONDENCIA CONTENIDOS')
            worksheet.write(row, col+11, 'CALIFICACIÓN FINAL')
            worksheet.write(row, col+12, 'RESULTADO DEL ANÁLISIS')
            
            analisis = Analisis.objects.filter(homologacion=registro)
            
            for i in analisis:
                row += 1
                worksheet.write(row, col, i.destino.codigo)
                worksheet.write(row, col+1, i.destino.nombre)
                worksheet.write(row, col+2, i.destino.nivel)
                worksheet.write(row, col+3, i.origen.codigo)
                worksheet.write(row, col+4, i.origen.nombre)
                worksheet.write(row, col+5, i.nota_aprobacion)
                worksheet.write(row, col+6, registro.origen.nota_maxima)
                worksheet.write(row, col+7, i.origen.horas)
                worksheet.write(row, col+8, i.periodo)
                worksheet.write(row, col+9, i.porcentaje_horas)
                worksheet.write(row, col+10, i.porcentaje_contenidos)
                worksheet.write(row, col+11, i.nota_final)
                if i.cumple:
                    worksheet.write(row, col+12, 'CUMPLE')
                else:
                    worksheet.write(row, col+12, 'NO CUMPLE')

        # Close the workbook before sending the data.
        workbook.close()

        # Rewind the buffer.
        output.seek(0)

        # Set up the Http response.
        filename = "homologaciones.xlsx"
        response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        
        return response

    actions = ['exportar']
    exportar.short_description = "Exportar homologaciones"


admin.site.register(Ies, IesAdmin)
admin.site.register(Carrera, CarreraAdmin)
admin.site.register(Asignatura, AsignaturaAdmin)
admin.site.register(Homologacion, HomologacionAdmin)