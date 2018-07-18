
from __future__ import unicode_literals
from django.db import models
import inspect
from census.models import Copy, CanonicalCopy, BaseCopy



def export_old_copies():
    
    old_copies = Copy.objects.filter(is_parent=True)

    base_copy_fields = set(f.name for f in BaseCopy._meta.get_fields())
    base_copy_fields &= set(f.name for f in Copy._meta.get_fields())

    base_copy_fields.discard('id')
    base_copy_fields.discard('pk')
    base_copy_fields.discard('created_by')

    for copy in old_copies:
        canonical_copy = CanonicalCopy()
        for f in base_copy_fields:

            setattr(canonical_copy, f, getattr(copy, f))
        canonical_copy.save()
