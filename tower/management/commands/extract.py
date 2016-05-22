import os
import tempfile
from subprocess import Popen

from django.core.management.base import BaseCommand
from django.conf import settings

from babel.messages.extract import (DEFAULT_KEYWORDS, extract_from_dir)
from translate.storage import po

from tower import split_context

# These are here for backwards compatibility with older iterations of
# tower.
from tower import extract_tower_python, extract_tower_template

DEFAULT_DOMAIN = 'all'

TEXT_DOMAIN = getattr(settings, 'TEXT_DOMAIN', 'messages')

# JINJA_CONFIG can be a callable or a dict.
if hasattr(settings.JINJA_CONFIG, '__call__'):
    JINJA_CONFIG = settings.JINJA_CONFIG()
else:
    JINJA_CONFIG = settings.JINJA_CONFIG

# By default, all the domains you speficy will be merged into one big
# messages.po file.  If you want to separate a domain from the main .po file,
# specify it in this list.  Make sure to include TEXT_DOMAIN in this list, even
# if you have other .po files you're generating
try:
    standalone_domains = settings.STANDALONE_DOMAINS
except AttributeError:
    standalone_domains = [TEXT_DOMAIN]

TOWER_KEYWORDS = dict(DEFAULT_KEYWORDS)

if hasattr(settings, 'TOWER_KEYWORDS'):
    TOWER_KEYWORDS.update(settings.TOWER_KEYWORDS)

OPTIONS_MAP = {
    '**.*': {'extensions': ",".join(JINJA_CONFIG['extensions'])},
}

COMMENT_TAGS = ['L10n:', 'L10N:', 'l10n:', 'l10N:']


def create_pounit(filename, lineno, message, comments):
    unit = po.pounit(encoding="UTF-8")
    if isinstance(message, tuple):
        _, s = split_context(message[0])
        c, p = split_context(message[1])
        unit.setsource([s, p])
        # Workaround for http://bugs.locamotion.org/show_bug.cgi?id=1385
        unit.target = [u"", u""]
    else:
        c, m = split_context(message)
        unit.setsource(m)
    if c:
        unit.msgctxt = ['"%s"' % c]
    if comments:
        for comment in comments:
            unit.addnote(comment, "developer")

    unit.addlocation("%s:%s" % (filename, lineno))
    return unit


def create_pofile_from_babel(extracted):
    try:
        if settings.TOWER_ADD_HEADERS:
            catalog = po.pofile()
        else:
            catalog = po.pofile(inputfile="")
    except AttributeError:
        catalog = po.pofile(inputfile="")

    for extracted_unit in extracted:
        # Babel 1.3 has an additional value: context.
        if len(extracted_unit) == 5:
            filename, lineno, message, comments, context = extracted_unit
        else:
            filename, lineno, message, comments = extracted_unit

        unit = create_pounit(filename, lineno, message, comments)
        catalog.addunit(unit)
    catalog.removeduplicates()
    return catalog


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--domain', '-d',
            default=DEFAULT_DOMAIN,
            dest='domain',
            help='The domain of the message files.  If "all" '
                 'everything will be extracted and combined into '
                 '%s.pot. (default: %%default).' % TEXT_DOMAIN)
        parser.add_argument('--output-dir', '-o',
            default=os.path.join(settings.ROOT, 'locale', 'templates',
                                'LC_MESSAGES'),
            dest='outputdir',
            help='The directory where extracted files will be placed. '
                 '(Default: %default)')
        parser.add_argument('-c', '--create',
            action='store_true',
            dest='create',
            default=False,
            help='Create output-dir if missing')

    def handle(self, *args, **options):
        domains = options.get('domain')
        outputdir = os.path.abspath(options.get('outputdir'))

        if not os.path.isdir(outputdir):
            if not options.get('create'):
                print("Output directory must exist (%s) unless -c option is "
                      "given. "
                      "Specify one with --output-dir" % outputdir)
                return "FAILURE\n"
            else:
                os.makedirs(outputdir)

        if domains == "all":
            domains = settings.DOMAIN_METHODS.keys()
        else:
            domains = [domains]

        root = settings.ROOT

        def callback(filename, method, options):
            if method != 'ignore':
                print("  %s" % filename)

        for domain in domains:

            print("Extracting all strings in domain %s..." % (domain))

            methods = settings.DOMAIN_METHODS[domain]
            extracted = extract_from_dir(root,
                                         method_map=methods,
                                         keywords=TOWER_KEYWORDS,
                                         comment_tags=COMMENT_TAGS,
                                         callback=callback,
                                         options_map=OPTIONS_MAP,
                                         )
            catalog = create_pofile_from_babel(extracted)
            if os.path.exists(outputdir):
                catalog.savefile(os.path.join(outputdir, '%s.pot' % domain))
            else:
                raise Exception("Expected %s to exist... BAILING" % outputdir)

        pot_files = []
        for i in [x for x in domains if x not in standalone_domains]:
            pot_files.append(os.path.join(outputdir, '%s.pot' % i))

        if len(pot_files) > 1:
            print("Concatenating the non-standalone domains into %s.pot" %
                  TEXT_DOMAIN)

            final_out = os.path.join(outputdir, '%s.pot' % TEXT_DOMAIN)

            # We add final_out back on because msgcat will combine all
            # specified files.  We'll redirect everything back in to
            # final_out in a minute.
            pot_files.append(final_out)

            meltingpot = tempfile.TemporaryFile()
            command = ["msgcat"] + pot_files
            p1 = Popen(command, stdout=meltingpot)
            p1.communicate()
            meltingpot.seek(0)

            # w+ truncates the file first
            with open(final_out, 'w+') as final:
                final.write(meltingpot.read())

            meltingpot.close()

            for i in [x for x in domains if x not in standalone_domains]:
                os.remove(os.path.join(outputdir, '%s.pot' % i))

        print('done')
