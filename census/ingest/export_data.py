import os
import unicodecsv
from census.models import Title, Edition, Issue, Copy

def mk_copy_row(c):
    return [c.issue.ESTC, c.Owner, 'null', c.Shelfmark, c.Local_Notes, c.prov_info, 'null']

def mk_issue_row(i):
    return [i.edition.title, i.edition.Edition_number, i.year, i.STC_Wing, i.ESTC, i.notes]

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

def export_copy_file(filename):
    copies = Copy.objects.all()
    rows = [['ESTC number', 'Library name', 'Lib VIAF id', 'shelfmark', 
            'copynote', 'prov info', 'prov info ID']]
    rows.extend(mk_copy_row(c) for c in copies)

    filename = check_filename(filename)
    with open(filename, 'wb') as op:
        unicodecsv.writer(op, encoding='utf-8').writerows(rows)

def export_issue_file(filename):
    issues = Issue.objects.all()
    rows = [['Title', 'Edn #', 'Date', 'STC/Wing', 'ESTC Cit #', 'Notes']]
    rows.extend(mk_issue_row(i) for i in issues)
    
    filename = check_filename(filename)
    with open(filename, 'wb') as op:
        unicodecsv.writer(op, encoding='utf-8').writerows(rows)
    
