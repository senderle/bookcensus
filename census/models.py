from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User, Group
from django.forms import ModelForm
from django.db.models.signals import post_save
from django.dispatch import receiver

class Title(models.Model):
	title = models.CharField(max_length=128, unique=True)
	Apocryphal = models.BooleanField(default=False)

	def __unicode__(self):
		return self.title

class Edition (models.Model):
	title = models.ForeignKey(Title)
	Edition_number = models.CharField(max_length=20, unique=False, null=True)
	Edition_format = models.CharField(max_length=10, null=True)
	def __str__(self):
		return "%s Edition %s" % (self.title, self.Edition_number)

class Issue (models.Model):
	edition = models.ForeignKey(Edition, unique=False)
	STC_Wing = models.CharField(max_length=20)
	ESTC = models.CharField(max_length=20)
	year = models.CharField(max_length=20, default=None)
	start_date = models.IntegerField(default=0)
	end_date = models.IntegerField(default=0)
	DEEP = models.IntegerField(default=0, null=True)
	notes = models.CharField(max_length=1000, default=None, null=True)
	Variant_Description = models.CharField(max_length=1000, null=True)
	def __str__(self):
		return "%s ESTC %s" % (self.edition, self.ESTC)

class Copy (models.Model):
	Owner = models.CharField(max_length=500)
	issue = models.ForeignKey(Issue, unique=False)
	thumbnail_URL = models.URLField(max_length=500, null=True)
	NSC = models.IntegerField(default=0, null=True)
	Shelfmark = models.CharField(max_length=500, default=None, null=True)
	Height = models.IntegerField(default=0, null=True)
	Width = models.IntegerField(default=0, null=True)
	Marginalia = models.CharField(max_length=100, null=True)
	Condition = models.CharField(max_length=200, default=None, null=True)
	Binding = models.CharField(max_length=200, default=None, null=True)
	Binder = models.CharField(max_length=40, default=None, null=True)
	Bookplate = models.CharField(max_length=40, default=None, null=True)
	Bookplate_Location = models.CharField(max_length=100, default=None, null=True)
	Bartlett1939 = models.IntegerField(default=0, null=True)
	Bartlett1939_Notes = models.CharField(max_length=1000, default=None, null=True)
	Bartlett1916 = models.IntegerField(default=0, null=True)
	Bartlett1916_Notes = models.CharField(max_length=1000, default=None, null=True)
	Lee_Notes = models.CharField(max_length=2000, default=None, null=True)
	Local_Notes=models.CharField(max_length=5000, default=None, null=True)
	created_by=models.ForeignKey(User, related_name="submitted_copies", default=1, null=True)
	prov_info=models.TextField(null=True, default=None)
	librarian_validated = models.BooleanField(default=False)
	admin_validated = models.BooleanField(default=False)
	is_parent=models.BooleanField(default=False)
	is_history=models.BooleanField(default=False)
	from_estc=models.BooleanField(default=False)
	false_positive_draft=models.NullBooleanField(default=None)
	false_positive=models.NullBooleanField(default=None)

	def __str__(self):
		return  "%s (%s)" % (self.issue, self.issue.year)
	class Meta:
		verbose_name_plural = "copies"

class ChildCopy(Copy):
	parent = models.ForeignKey(Copy, related_name='children', default=None, null=True)
	held_by_library=models.BooleanField(default=False)

class CopyHistory(Copy):
	stored_copy = models.ForeignKey(Copy, related_name="copy_history", default=None, null=True)  #copy of which the current object is the history of
	date_created = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	def __unicode__(self):
		return self.user.username
	def delete(self, *args, **kwargs):
		self.user.delete()
		return super(UserProfile,self).delete(*args, **kwargs)

class Entity(models.Model):
	name = models.CharField(max_length=200)
	notes = models.CharField(max_length=500)
	def __str__(self):
		return "%s" % (self.name)
	class Meta:
		verbose_name_plural = "entities"

class Transaction(models.Model):
	copy = models.ForeignKey(Copy, on_delete=models.CASCADE)
	buyer = models.ForeignKey(Entity, related_name="entity_buyer", max_length=100)
	seller = models.ForeignKey(Entity, related_name="entity_seller", max_length=100)
	date = models.DateField()
	price = models.DecimalField(max_digits = 10, decimal_places=2)
	def __str__(self):
		return "Sold from %s to %s" % (self.seller, self.buyer)

class UserDetail(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	affiliation = models.CharField(max_length=255, null=True)
	group=models.ForeignKey(Group, default=1)

	def __str__(self):
		return self.user.username
	class Meta:
		verbose_name_plural = "user details"

@receiver(post_save, sender=User)
def create_user_detail(sender, instance, created, **kwargs):
	if created:
		UserDetail.objects.create(user=instance)

#The following models are not used right now. Need further information.
class Provenance (models.Model):
	copy = models.ForeignKey(Copy, on_delete=models.CASCADE)
	name = models.CharField(max_length=40)
	bio = models.CharField(max_length=1000)
	def __str__(self):
		return "%s %s" % (self.copy, self.name)
class BookPlate (models.Model):
	copy = models.ForeignKey(Copy, on_delete=models.CASCADE)
	text = models.CharField(max_length=100)
	def __str__(self):
		return  "%s" % (self.text)
class BookPlate_Location (models.Model):
	copy = models.ForeignKey(Copy, on_delete=models.CASCADE)
	Location = models.CharField(max_length=100)
	def __str__(self):
		return  "%s" % (self.Location)
class Transfer(models.Model):
	copy = models.ForeignKey(Copy, on_delete=models.CASCADE)
	bleh = models.CharField(max_length=100)
	def __str__(self):
		return  "%s" % (self.bleh)
class Transfer_Value (models.Model):
	copy = models.ForeignKey(Copy, on_delete=models.CASCADE)
	Value = models.CharField(max_length=100)
	def __str__(self):
		return  "%s" % (self.Value)
