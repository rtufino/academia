import io 
import xlsxwriter

from django.contrib import admin
from django.forms import Textarea, TextInput
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

    fields = ('destino', 'origen', 'periodo', 'nota_aprobacion', 'porcentaje_horas', 'porcentaje_contenidos', 'nota_final', 'cumple')

    formfield_overrides = {
        models.DecimalField: {'widget': TextInput(attrs={'size':'5'})},
        models.CharField: {'widget': TextInput(attrs={'size':15})},
    }

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        field = formset.form.base_fields["origen"]
        field.widget.can_add_related = False
        # field.widget.can_change_related = False
        field.widget.can_delete_related = False
        field.widget.can_view_related = False
        field = formset.form.base_fields["destino"]
        field.widget.can_add_related = False
        # field.widget.can_change_related = False
        field.widget.can_delete_related = False
        field.widget.can_view_related = False
        return formset
    
    def formfield_for_foreignkey(self,  db_field, request, **kwargs):
        try:
            h = Homologacion.objects.get(pk=request.resolver_match.kwargs.get('object_id')) 
            if db_field.name == 'origen':
                kwargs['queryset'] = Asignatura.objects.filter(carrera=h.origen).order_by('nivel', 'nombre')
            if db_field.name == 'destino':
                kwargs['queryset'] = Asignatura.objects.filter(carrera=h.destino).order_by('nivel', 'nombre')
        except:
            pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class HomologacionAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'apellidos', 'nombres', 'fecha', 'origen', 'destino', 'terminada')
    inlines = [AnalisisAdminInLine,]

    def exportar(self, request, queryset):
        output = io.BytesIO()

        workbook = xlsxwriter.Workbook(output)

        row = 0
        col = 0

        # Add a bold format to use to highlight cells.
        gris = workbook.add_format({'bold': True, 'bg_color': 'cccccc'})
        amarrillo = workbook.add_format({'bold': True, 'bg_color': 'ffffd7'})
        azul = workbook.add_format({'bold': True, 'bg_color': 'dee6ef'})
        bold = workbook.add_format({'bold': True})

        # Add a number format for cells with percent.
        percent = workbook.add_format({'num_format': '0.%'})

        decimal = workbook.add_format({'num_format': '0.00'})


        for registro in queryset:
            
            nombre = registro.nombres.split()[0] + ' ' + registro.apellidos.split()[0]

            worksheet = workbook.add_worksheet(name=nombre)
            
            row = 0
            col = 0

            worksheet.write(row, col, 'CÉDULA', bold)
            worksheet.write(row+1, col, 'NOMBRES', bold)
            worksheet.write(row+2, col, 'APELLIDOS', bold)
            worksheet.write(row+3, col, 'CARRERA ORIGEN', bold)
            worksheet.write(row+4, col, 'CARRERA DESTINO', bold)

            worksheet.write(row, col+1, registro.cedula)
            worksheet.write(row+1, col+1, registro.nombres)
            worksheet.write(row+2, col+1, registro.apellidos)
            worksheet.write(row+3, col+1, registro.origen.__str__())
            worksheet.write(row+4, col+1, registro.destino.__str__())

            row += 6

            worksheet.write(row, col, 'CÓDIGO', gris)
            worksheet.write(row, col+1, 'NOMBRE', gris)
            worksheet.write(row, col+2, 'NIVEL', gris)
            worksheet.write(row, col+3, 'CÓDIGO', amarrillo)
            worksheet.write(row, col+4, 'NOMBRE', amarrillo)
            worksheet.write(row, col+5, 'CALIFICACIÓN CON LA QUE APRUEBA LA ASIGNATURA', amarrillo)
            worksheet.write(row, col+6, 'CALIFICACIÓN TOTAL DE APROBACIÓN DE LA IES ORIGEN', amarrillo)
            worksheet.write(row, col+7, 'NÚMERO DE HORAS / CRÉDITOS', amarrillo)
            worksheet.write(row, col+8, 'FECHA / PERÍODO ACADÉMICO DE APROBACIÓN', amarrillo)
            worksheet.write(row, col+9, 'PORCENTAJE DE CORRESPONDENCIA HORAS', azul)
            worksheet.write(row, col+10, 'PORCENTAJE DE CORRESPONDENCIA CONTENIDOS', azul)
            worksheet.write(row, col+11, 'CALIFICACIÓN FINAL', azul)
            worksheet.write(row, col+12, 'RESULTADO DEL ANÁLISIS', azul)
            
            analisis = Analisis.objects.filter(homologacion=registro)
            
            for i in analisis:
                row += 1
                worksheet.write(row, col, i.destino.codigo)
                worksheet.write(row, col+1, i.destino.nombre)
                worksheet.write(row, col+2, i.destino.nivel)
                worksheet.write(row, col+3, i.origen.codigo)
                worksheet.write(row, col+4, i.origen.nombre)
                worksheet.write(row, col+5, i.nota_aprobacion, decimal)
                worksheet.write(row, col+6, registro.origen.nota_maxima, decimal)
                worksheet.write(row, col+7, i.origen.horas)
                worksheet.write(row, col+8, i.periodo)
                worksheet.write(row, col+9, (i.porcentaje_horas/100), percent)
                worksheet.write(row, col+10, (i.porcentaje_contenidos/100), percent)
                worksheet.write(row, col+11, i.nota_final, decimal)
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