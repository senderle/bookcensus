from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Title)
admin.site.register(Edition)
admin.site.register(UserProfile)
admin.site.register(Issue)
admin.site.register(Entity)
admin.site.register(Transaction)
admin.site.register(UserDetail)
admin.site.register(CopyHistory)
admin.site.register(ChildCopy)

class BookPlatezInline(admin.StackedInline):
	model = BookPlate
	fk_name = 'copy'
class BookPlateLocationInline(admin.StackedInline):
	model = BookPlate_Location
	fk_name = 'copy'
class TransferInline(admin.StackedInline):
	model = Transfer
	fk_name = 'copy'
class TransferValueInline(admin.StackedInline):
	model = Transfer_Value
	fk_name = 'copy'
class ProvenanceInline(admin.StackedInline):
	model = Provenance
	fk_name = 'copy'

class CopyAdmin(admin.ModelAdmin):
	inlines = [
		 BookPlatezInline,
		 BookPlateLocationInline,
		 TransferInline,
		 TransferValueInline,
		 ProvenanceInline,
	]

admin.site.register(Copy, CopyAdmin)
admin.site.register(BookPlate)
admin.site.register(BookPlate_Location)
admin.site.register(Transfer)
admin.site.register(Transfer_Value)
admin.site.register(Provenance)
