from django.contrib import admin
#from django_extensions.admin import ForeignKeyAutocompleteAdmin

# Register your models here.
from .models import *

admin.site.register(StaticPageText)
admin.site.register(Title)
admin.site.register(Issue)
admin.site.register(Edition)
admin.site.register(Copy)
admin.site.register(UserProfile)
admin.site.register(UserDetail)

#admin.site.register(LibrarianEmail)

@admin.register(DraftCopy)
class DraftCopyAdmin(admin.ModelAdmin):
    raw_id_fields = ("parent",)

admin.site.register(CanonicalCopy)
'''
class CanonicalCopyAdmin(admin.ModelAdmin):
    search_fields = ("Owner",)
'''
admin.site.register(HistoryCopy)
admin.site.register(FalseCopy)
admin.site.register(BaseCopy)
#admin.site.register(CanonicalCopyAdmin)
