from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User, Group
from django.forms import ModelForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms
# from tinymce import models as tinymce_models

### Main Site Operations ###

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    def __unicode__(self):
        return self.user.username
    def delete(self, *args, **kwargs):
        self.user.delete()
        return super(UserProfile,self).delete(*args, **kwargs)

class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    affiliation = models.CharField(max_length=255, null=True)
    group=models.ForeignKey(Group, default=1)

    def __str__(self):
        return self.user.username
    class Meta:
        verbose_name_plural = "user details"
'''
class LibrarianEmail(models.Model):
    email = models.EmailField(max_length=200)

    def __str__(self):
        return self.email
    class Meta:
        verbose_name_plural = "trusted emails"
'''
class StaticPageText(models.Model):
    content = models.TextField(null=True, blank=True, default=None)
    #htmlcontent = tinymce_models.HTMLField()
    viewname = models.CharField(max_length=255, default='', null=True, blank=True)

    def __str__(self):
        return self.viewname
    class Meta:
        verbose_name_plural = "Static Pages"

@receiver(post_save, sender=User)
def create_user_detail(sender, instance, created, **kwargs):
    if created:
        UserDetail.objects.create(user=instance)

### Core Data Tables ###

class Title(models.Model):
    title = models.CharField(max_length=128, unique=True)
    Apocryphal = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

class Edition (models.Model):
    title = models.ForeignKey(Title)
    Edition_number = models.CharField(max_length=20, unique=False, null=True, blank=True)
    Edition_format = models.CharField(max_length=10, null=True, blank=True)
    def __str__(self):
        return "%s Edition %s" % (self.title, self.Edition_number)

class Issue (models.Model):
    edition = models.ForeignKey(Edition, unique=False)
    STC_Wing = models.CharField(max_length=20)
    ESTC = models.CharField(max_length=20)
    year = models.CharField(max_length=20, default=None)
    start_date = models.IntegerField(default=0)
    end_date = models.IntegerField(default=0)
    DEEP = models.CharField(max_length=20, default='', null=True, blank=True)
    notes = models.TextField(null=True, blank=True, default=None)
    Variant_Description = models.CharField(max_length=1000, null=True, blank=True)
    def ESTC_as_list(self):
        estc_list = self.ESTC.split('; ')
        return [(estc, (i + 1) == len(estc_list))
                for i, estc in enumerate(estc_list)]

    def DEEP_as_list(self):
        deep_list = self.DEEP.split('; ')
        return [(depp, (i + 1) == len(deep_list))
                for i, deep in enumerate(deep_list)]


    def __str__(self):
        return "%s ESTC %s" % (self.edition, self.ESTC)

class Location(models.Model):
    name = models.CharField(max_length=500)
    def __unicode__(self):
        return self.name

# Essential fields for all copies.
class BaseCopy(models.Model):
    Owner = models.CharField(max_length=500)
    location = models.ForeignKey(Location, unique=False, null=True, blank=True)
    issue = models.ForeignKey(Issue, unique=False)
    thumbnail_URL = models.URLField(max_length=500, null=True, blank=True)
    NSC = models.IntegerField(default=0, null=True)
    Shelfmark = models.CharField(max_length=500, default=None, null=True, blank=True)
    Height = models.FloatField(default=0, null=True)
    Width = models.FloatField(default=0, null=True)
    Marginalia = models.TextField(null=True, blank=True, default=None)
    Condition = models.CharField(max_length=200, default=None, null=True, blank=True)
    Binding = models.CharField(max_length=200, default=None, null=True, blank=True)
    Binder = models.CharField(max_length=40, default=None, null=True, blank=True)
    Bookplate = models.CharField(max_length=40, default=None, null=True, blank=True)
    Bookplate_Location = models.CharField(max_length=100, default=None, null=True, blank=True)
    Bartlett1939 = models.IntegerField(default=0, null=True)
    Bartlett1939_Notes = models.TextField(null=True, blank=True, default=None)
    Bartlett1916 = models.IntegerField(default=0, null=True)
    Bartlett1916_Notes = models.TextField(null=True, blank=True, default=None)
    Lee_Notes = models.TextField(null=True, blank=True, default=None)
    Local_Notes = models.TextField(null=True, blank=True, default=None)
    created_by = models.ForeignKey(User, related_name="user_submitted_copies", default=1, null=True)
    prov_info = models.TextField(null=True, blank=True, default=None)
    bibliography = models.TextField(null=True, blank=True, default=None)
    from_estc = models.BooleanField(default=False)
    location_verified = models.BooleanField(default=False)

    def __str__(self):
        return  "%s (%s)" % (self.issue, self.issue.year)
    class Meta:
        verbose_name_plural = "Base copies"

# Copy records that have been ruled spurious. These records should
# be preserved across versions of the app if possible.
class FalseCopy(BaseCopy):
    class Meta:
        verbose_name_plural = "False copies"

# Copy records that we are treating as accurate. These records *must*
# be preserved across versions of the app.
class CanonicalCopy(BaseCopy):
    class Meta:
        verbose_name_plural = "Canonical copies"

# Copy records that are modified versions of records from CanonicalCopy.
# These are working records and historical versions that we don't treat
# as vital for preservation.
class DraftCopy(BaseCopy):
    parent = models.ForeignKey(CanonicalCopy, related_name='drafts', default=None, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "Draft copies"

class HistoryCopy(BaseCopy):
    parent = models.ForeignKey(CanonicalCopy, related_name='versions', default=None, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "History copies"


### Copy Management Classes/Callables ###

class LinkedCopyCreate(object):
    def __init__(self, source_model, target_model, base_model):
        self.source_model = source_model
        self.target_model = target_model
        self.base_model = base_model
        self.copy_fields = set(f.name for f in base_model._meta.fields)
        self.copy_fields.discard('id')
        self.copy_fields.discard('pk')
    def __call__(self, source):
        if not isinstance(source, self.source_model):
            raise ValueError('Can only copy instances of {}'.format(self.source_model))
        new = self.target_model()
        for f in self.copy_fields:
            setattr(new, f, getattr(source, f))
        new.parent = source
        new.save()
        return new

create_draft = LinkedCopyCreate(CanonicalCopy, DraftCopy, BaseCopy)
create_history = LinkedCopyCreate(CanonicalCopy, HistoryCopy, BaseCopy)

class LinkedCopyUpdate(object):
    def __init__(self, source_model, target_model, record_model, base_model):
        self.source_model = source_model
        self.target_model = target_model
        self.record_model = record_model
        self.base_model = base_model
        self.create_record = LinkedCopyCreate(target_model, record_model, base_model)
        self.copy_fields = set(f.name for f in base_model._meta.fields)
        self.copy_fields.discard('id')
        self.copy_fields.discard('pk')
    def __call__(self, source):
        if not isinstance(source, self.source_model):
            raise ValueError('Can only update from instances of {}'.format(self.source_model))
        if not isinstance(source.parent, self.target_model):
            raise ValueError('Can only update to instances of {}, but the parent of {} is a {}'.format(self.target_model, source, type(source.parent)))
        parent = source.parent
        print(parent.id)
        print(source.id)
        self.create_record(parent)
        for f in self.copy_fields:
            setattr(parent, f, getattr(source, f))
        print(parent.id)
        print(source.id)

        parent.save()
        source.delete()

draft_to_canonical_update = LinkedCopyUpdate(DraftCopy, CanonicalCopy, HistoryCopy, BaseCopy)
history_to_canonical_update = LinkedCopyUpdate(HistoryCopy, CanonicalCopy, DraftCopy, BaseCopy)

class LinkedCopyCreateParent(object):
    def __init__(self, source_model, target_model, base_model):
        self.source_model = source_model
        self.target_model = target_model
        self.base_model = base_model
        self.copy_fields = set(f.name for f in base_model._meta.fields)
        self.copy_fields.discard('id')
        self.copy_fields.discard('pk')
    def __call__(self, source):
        if not isinstance(source, self.source_model):
            raise ValueError('Can only copy instances of {}'.format(self.source_model))
        if source.parent:
            raise ValueError('Can only create parents for objects that don\'t have one!')
        new = self.target_model()
        for f in self.copy_fields:
            setattr(new, f, getattr(source, f))
        source.parent = new
        new.save()

draft_to_canonical_create = LinkedCopyCreateParent(DraftCopy, CanonicalCopy, BaseCopy)

class ParentCopyMove(object):
    def __init__(self, source_model, target_model, base_model):
        self.source_model = source_model
        self.target_model = target_model
        self.base_model = base_model
        self.copy_fields = set(f.name for f in base_model._meta.fields)
        self.copy_fields.discard('id')
        self.copy_fields.discard('pk')
    def __call__(self, source):
        if not isinstance(source, self.source_model):
            raise ValueError('Can only copy instances of {}'.format(self.source_model))
        new = self.target_model()
        for f in self.copy_fields:
            setattr(new, f, getattr(source, f))
        new.save()
        source.delete()

canonical_to_fp_move = ParentCopyMove(CanonicalCopy, FalseCopy, BaseCopy)

### Old Models (Unused or to be retired) ###

class Copy(models.Model):
    Owner = models.CharField(max_length=500)
    issue = models.ForeignKey(Issue, unique=False)
    thumbnail_URL = models.URLField(max_length=500, null=True, blank=True)
    NSC = models.IntegerField(default=0, null=True)
    Shelfmark = models.CharField(max_length=500, default=None, null=True, blank=True)
    Height = models.FloatField(default=0, null=True)
    Width = models.FloatField(default=0, null=True)
    Marginalia = models.TextField(null=True, blank=True, default=None)
    Condition = models.CharField(max_length=200, default=None, null=True, blank=True)
    Binding = models.CharField(max_length=200, default=None, null=True, blank=True)
    Binder = models.CharField(max_length=40, default=None, null=True, blank=True)
    Bookplate = models.CharField(max_length=40, default=None, null=True, blank=True)
    Bookplate_Location = models.CharField(max_length=100, default=None, null=True, blank=True)
    Bartlett1939 = models.IntegerField(default=0, null=True)
    Bartlett1939_Notes = models.TextField(null=True, blank=True, default=None)
    Bartlett1916 = models.IntegerField(default=0, null=True)
    Bartlett1916_Notes = models.TextField(null=True, blank=True, default=None)
    Lee_Notes = models.TextField(null=True, blank=True, default=None)
    Local_Notes = models.TextField(null=True, blank=True, default=None)
    created_by = models.ForeignKey(User, related_name="submitted_copies", default=1, null=True)
    prov_info = models.TextField(null=True, blank=True, default=None)
    bibliography = models.TextField(null=True, blank=True, default=None)
    librarian_validated = models.BooleanField(default=False)
    admin_validated = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_history = models.BooleanField(default=False)
    from_estc = models.BooleanField(default=False)
    false_positive_draft = models.NullBooleanField(default=None)
    false_positive = models.NullBooleanField(default=None)

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

# (Currently Unused)
class Entity(models.Model):
    name = models.CharField(max_length=200)
    notes = models.CharField(max_length=500)
    def __str__(self):
        return "%s" % (self.name)
    class Meta:
        verbose_name_plural = "entities"

# (Currently Unused)
class Transaction(models.Model):
    copy = models.ForeignKey(Copy, on_delete=models.CASCADE)
    buyer = models.ForeignKey(Entity, related_name="entity_buyer", max_length=100)
    seller = models.ForeignKey(Entity, related_name="entity_seller", max_length=100)
    date = models.DateField()
    price = models.DecimalField(max_digits = 10, decimal_places=2)
    def __str__(self):
        return "Sold from %s to %s" % (self.seller, self.buyer)

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

class ContactForm(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, default="")
    subject = models.CharField(max_length=200, default="")
    message = models.TextField(default="")
    guardian = models.CharField(max_length=50, default="", blank=True) #field for honeypot captcha
    def __str__(self):
        return  "%s" % (self.name)
