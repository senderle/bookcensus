from django.core.management.base import BaseCommand, CommandError
from census.ingest import export_data

class Command(BaseCommand):
    help = ('Export a basic version of the current database. '
            'NOTE: This does not currently preserve important '
            'information about where the data came from, and so '
            'librarian validated data will not be identified '
            'as such, and will have to be re-checked.')

    def add_arguments(self, parser):
        parser.add_argument('issue_file')
        parser.add_argument('copy_file')

    def handle(self, *args, **options):
        export_data.export_issue_file(options['issue_file'])
        export_data.export_copy_file(options['copy_file'])
