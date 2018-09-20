from django.contrib import admin
#from django_extensions.admin import ForeignKeyAutocompleteAdmin

# Register your models here.
# from .models import *
import models

admin.site.register(models.StaticPageText)
admin.site.register(models.Title)
admin.site.register(models.Issue)
admin.site.register(models.Edition)
admin.site.register(models.UserProfile)
admin.site.register(models.UserDetail)

admin.site.register(models.ContactForm)
admin.site.register(models.Location)
#admin.site.register(LibrarianEmail)

@admin.register(models.DraftCopy)
class DraftCopyAdmin(admin.ModelAdmin):
    raw_id_fields = ("parent",)

admin.site.register(models.CanonicalCopy)
admin.site.register(models.HistoryCopy)
admin.site.register(models.FalseCopy)
admin.site.register(models.BaseCopy)

### The below are all unused currently.

# admin.site.register(BookPlate)
# admin.site.register(BookPlate_Location)
# admin.site.register(Transfer)
# admin.site.register(Transfer_Value)
# admin.site.register(Provenance)
# admin.site.register(CanonicalCopyAdmin)
