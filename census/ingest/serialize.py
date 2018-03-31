import os
import codecs
from census.models import Title, Edition, Issue, Copy
from django.core.serializers import serialize, deserialize

# This defines the primary backup dataset. There are lots of
# other tables, but we regard all of them as containing ephemeral
# data subject to loss at any time. *This* data is unrecoverable
# if lost, and is therefore the first priority for backups. It
# should be saved to files tracked by version control -- the
# quantity will never be so large that it won't fit in a
# standard GitHub repository.

_canonical_models = [
    ('copies', Copy),
    ('issues', Issue),
    ('editions', Edition),
    ('titles', Title),
]

def get_canonical_models(export=False):
    if export:
        models = [[name, model.objects.all()] for name, model in _canonical_models]
        models[0][1] = models[0][1].filter(is_parent=True)  # Only parent copies are canonical
        return models
    else:
        return _canonical_models

def check_filename(f):
    new_f = f
    if os.path.exists(f):
        n = 1
        new_f, ext = os.path.splitext(f)
        new_f_template = new_f + '-{}{}'
        new_f = new_f_template.format(n, ext)
        while os.path.exists(new_f):
            n += 1
            new_f = new_f_template.format(n, ext)
    return new_f

def export_query_json(filename, queryset):
    data = serialize('json', queryset)

    filename = check_filename(filename)
    with codecs.open(filename, 'w', encoding='utf-8') as op:
        op.write(data)

def export_canon_json(filename_base='backup'):
    for name, query in get_canonical_models(export=True):
        filename = '{}_{}.json'.format(filename_base, name)
        export_query_json(filename, query)

def import_query_json(filename, queryset):
    with codecs.open(filename, 'r', encoding='utf-8') as ip:
        data = ip.read()

    for row in deserialize('json', data):
        row.save()

def import_canon_json(filename_base='backup'):
    canonical_models = [('{}_{}.json'.format(filename_base, name), model)
                        for name, model in get_canonical_models(export=False)]
    if all(os.path.isfile(filename) for filename, model in canonical_models):
        for filename, model in canonical_models:
            import_query_json(filename, model)
