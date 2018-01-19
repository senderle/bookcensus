from django.core.management.base import BaseCommand, CommandError
from census.ingest import load_data
from census.models import Copy, Issue

class Command(BaseCommand):
    help = 'Populate an empty database with an archive dump.'

    def add_arguments(self, parser):
        parser.add_argument('issue_file')
        parser.add_argument('copy_file')

    def handle(self, *args, **options):
        if Copy.objects.all().count() > 0 or Issue.objects.all().count() > 0:
            raise CommandError('Cowardly refusing to modify '
                               'a non-empty database.')
        else:
            load_data.read_issue_file(options['issue_file'])
            load_data.read_copy_file(options['copy_file'])
