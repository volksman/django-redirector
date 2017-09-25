from django.core.management.base import BaseCommand

from django.contrib.redirects.models import Redirect as ContribRedirect

from redirector.models import Redirect

class Command(BaseCommand):
    help = 'Moves redirects from old contrib.redirects to new format'

    def handle(self, *args, **options):
        current = ContribRedirect.objects.all()
        for redir in current:
            new = Redirect(
                originating_url=redir.old_path,
                redirect_to_url=redir.new_path,
                redirect_type='301',
                site_id=1
            )
            new.save()
