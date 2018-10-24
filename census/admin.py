from django.contrib import admin
#from django_extensions.admin import ForeignKeyAutocompleteAdmin

# Register your models here.
# from .models import *
from . import models

admin.site.register(models.StaticPageText)

@admin.register(models.Title)
class TitleAdmin(admin.ModelAdmin):
    ordering = ('title',)

admin.site.register(models.Issue)
admin.site.register(models.Edition)
admin.site.register(models.UserProfile)
admin.site.register(models.UserDetail)

admin.site.register(models.ContactForm)

@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    ordering = ('name',)

@admin.register(models.DraftCopy)
class DraftCopyAdmin(admin.ModelAdmin):
    raw_id_fields = ("parent",)

admin.site.register(models.CanonicalCopy)

@admin.register(models.HistoryCopy)
class HistoryCopyAdmin(admin.ModelAdmin):
    raw_id_fields = ("parent",)

admin.site.register(models.FalseCopy)
admin.site.register(models.BaseCopy)

### The below are all unused currently.

# admin.site.register(BookPlate)
# admin.site.register(BookPlate_Location)
# admin.site.register(Transfer)
# admin.site.register(Transfer_Value)
# admin.site.register(Provenance)
# admin.site.register(CanonicalCopyAdmin)
