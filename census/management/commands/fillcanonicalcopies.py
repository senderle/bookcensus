from django.core.management.base import BaseCommand, CommandError
from census.ingest.cannonical_copy import export_old_copies

class Command(BaseCommand):
    help = ('Filter those from the Copy model and fill the CanonicalCopy'
            'NOTE: This does not currently preserve important '
            'information about where the data came from, and so '
            'librarian validated data will not be identified '
            'as such, and will have to be re-checked.')

    def add_arguments(self, parser):
        #parser.add_argument('json_basename')
        pass

    def handle(self, *args, **options):
        export_old_copies()
