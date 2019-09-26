from django.contrib import admin, auth
from django.conf import settings

from . import models

### Administrative Tables

class UserInlineAdmin(admin.StackedInline):
    model = models.UserDetail

admin.site.unregister(auth.get_user_model())
@admin.register(auth.get_user_model())
class UserDetailAdmin(admin.ModelAdmin):
    list_display = ['username']
    inlines = (UserInlineAdmin,)

@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    ordering = ('name',)

admin.site.register(models.StaticPageText)

@admin.register(models.ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    readonly_fields = ('date_submitted',)

### Core Data Tables

# Provenance tables

class ProvenanceOwnershipInline(admin.TabularInline):
    model = models.ProvenanceOwnership
    autocomplete_fields = ('copy', 'owner')
    extra = 1

@admin.register(models.ProvenanceName)
class ProvenanceNameAdmin(admin.ModelAdmin):
    ordering = ('name',)
    search_fields = ('name',)
    inlines = (ProvenanceOwnershipInline,)

@admin.register(models.ProvenanceOwnership)
class ProvenanceOwnershipAdmin(admin.ModelAdmin):
    autocomplete_fields = ('copy', 'owner')

# Higher-level FRBR categories

@admin.register(models.Title)
class TitleAdmin(admin.ModelAdmin):
    ordering = ('title',)
admin.site.register(models.Issue)
admin.site.register(models.Edition)

# Copy tables

@admin.register(models.CanonicalCopy)
class CanonicalCopyAdmin(admin.ModelAdmin):
    inlines = (ProvenanceOwnershipInline,)
    search_fields = ('NSC', 'issue__edition__title__title')

admin.site.register(models.FalseCopy)
admin.site.register(models.BaseCopy)
@admin.register(models.DraftCopy)
class DraftCopyAdmin(admin.ModelAdmin):
    raw_id_fields = ("parent",)

@admin.register(models.RejectedDraftCopy)
class RejectedDraftCopyAdmin(admin.ModelAdmin):
    raw_id_fields = ("parent",)

@admin.register(models.HistoryCopy)
class HistoryCopyAdmin(admin.ModelAdmin):
    raw_id_fields = ("parent",)

### The below are all unused currently.

# admin.site.register(BookPlate)
# admin.site.register(BookPlate_Location)
# admin.site.register(Transfer)
# admin.site.register(Transfer_Value)
# admin.site.register(Provenance)
# admin.site.register(CanonicalCopyAdmin)
