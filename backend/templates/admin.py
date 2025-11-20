from django.contrib import admin
from .models import Template, TemplateSection, TemplateVariable

class TemplateSectionInline(admin.StackedInline):
    model = TemplateSection
    extra = 0

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'created_at')
    inlines = [TemplateSectionInline]

@admin.register(TemplateVariable)
class TemplateVariableAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_value')
