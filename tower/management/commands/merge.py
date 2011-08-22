import os
import sys
from optparse import make_option
from subprocess import Popen
from tempfile import TemporaryFile

from django.core.management.base import BaseCommand
from django.conf import settings

try:
    domains = settings.STANDALONE_DOMAINS
except AttributeError:
    domains = [settings.TEXT_DOMAIN]

class Command(BaseCommand):

    """Updates all locales' PO files by merging them with the POT files.

    The command looks for POT files in locale/templates/LC_MESSAGES, which is
    where software like Verbatim looks for them as well.

    For a given POT file, if a corresponding PO file doesn't exist for a
    locale, the command will initialize it with `msginit`. This guarantees
    that the newly created PO file has proper gettext metadata headers.

    During merging (or initializing), the command will also look in
    `locale/compendia` for a locale-specific compendium of translations
    (serving as a translation memory of sorts). The compendium file must
    be called `${locale}.compendium`, e.g. `es_ES.compendium` for Spanish.
    The translations in the compendium will be used by gettext for fuzzy
    matching.

    """
    option_list = BaseCommand.option_list + (
             make_option('-c', '--create',
                    action="store_true", dest='create', default=False,
                    help='Create locale subdirectories'),

            )
    def handle(self, *args, **options):

        locale_dir = os.path.join(settings.ROOT, 'locale')

        if options.get('create'):
            for lang in getattr(settings, 'LANGUAGES', []):
                d = os.path.join(locale_dir, lang.replace('-', '_'),
                                 'LC_MESSAGES')
                if not os.path.exists(d):
                    os.makedirs(d)

        for domain in domains:

            print "Merging %s strings to each locale..." % domain
            domain_pot = os.path.join(locale_dir, 'templates', 'LC_MESSAGES',
                                      '%s.pot' % domain)
            if not os.path.isfile(domain_pot):
                sys.exit("Can't find %s.pot" % domain)

            for locale in os.listdir(locale_dir):
                if (not os.path.isdir(os.path.join(locale_dir, locale)) or
                    locale.startswith('.') or
                    locale == 'templates' or
                    locale == 'compendia'):
                            continue

                compendium = os.path.join(locale_dir, 'compendia',
                                          '%s.compendium' % locale)
                domain_po = os.path.join(locale_dir, locale, 'LC_MESSAGES',
                                         '%s.po' % domain)

                if not os.path.isfile(domain_po):
                    print " Can't find (%s).  Creating..." % (domain_po)
                    p1 = Popen(["msginit",
                                "--no-translator",
                                "--locale=%s" % locale,
                                "--input=%s" % domain_pot,
                                "--output-file=%s" % domain_po,
                                "--width=200",])
                    p1.communicate()

                print "Merging %s.po for %s" % (domain, locale)

                domain_pot_file = open(domain_pot)

                if locale == "en_US":
                    enmerged = TemporaryFile('w+t')
                    p2 = Popen(["msgen", "-"], stdin=domain_pot_file,
                            stdout=enmerged)
                    p2.communicate()
                    mergeme = enmerged
                else:
                    mergeme = domain_pot_file

                mergeme.seek(0)
                command = ["msgmerge",
                           "--update",
                           "--width=200",
                           domain_po,
                           "-"]
                if os.path.isfile(compendium):
                    print "(using a compendium)"
                    command.insert(1, '--compendium=%s' % compendium)
                p3 = Popen(command, stdin=mergeme)
                p3.communicate()
                mergeme.close()
            print "Domain %s finished" % domain

        print "All finished"

Command.help = Command.__doc__
