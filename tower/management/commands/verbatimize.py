import os
from optparse import make_option

from django.core.management.base import BaseCommand

from manage import settings

class Command(BaseCommand):

    """Moves the POT files into `locale/templates/LC_MESSAGES`.

    This will move the POT files created by tower's `extract` command in
    the locale directory to locale/templates/LC_MESSAGES which is recognized
    by Verbatim as a special directory for POT files. Optionally, the command
    can also remove the "z-" prefix from the filenames and in one special case,
    will rename "z-keys.pot" to "messages.pot" altogether.
    
    """

    option_list = BaseCommand.option_list + (
        make_option('--rename', dest='rename', action="store_true",
                    help='Rename z-foo.pot to foo.pot.'),  
        )

    def handle(self, *args, **options):

        locale_dir = os.path.join(settings.ROOT, 'locale')

        print "Copying the POT files..."
        for pot in os.listdir(locale_dir):
            if (not os.path.isfile(os.path.join(locale_dir, pot)) or
                not pot.endswith('.pot')):
                continue
            if options.get('rename', False) is True:
                new_pot = 'messages.pot' if pot == 'z-keys.pot' else pot.lstrip('z-')
            else:
                new_pot = pot
            template_pot = os.path.join(locale_dir, 'templates', 'LC_MESSAGES', new_pot)
            try:
                # Try to remove the old file first, or os.rename will raise 
                # an exception on Windows
                os.remove(template_pot)
            except OSError:
                pass
            os.rename(os.path.join(locale_dir, pot), template_pot)
            print "  Copied %s to %s" % (pot, template_pot)
        print "All done"
        
Command.help = Command.__doc__
