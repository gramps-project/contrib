#! /usr/bin/env python
"""
make.py for Gramps addons.

Examples: 
   python make.py init AddonDirectory

      Creates the initial directories for the addon.

   python make.py init AddonDirectory fr

      Creates the initial empty AddonDirectory/po/fr-local.po file
      for the addon.

   python make.py update AddonDirectory fr

      Updates AddonDirectory/po/fr-local.po with the latest
      translations.

   python make.py build AddonDirectory

      Build ../download/AddonDirectory.addon.tgz

   python make.py build all

      Build ../download/*.addon.tgz

   python make.py compile AddonDirectory
   python make.py compile all

      Compiles AddonDirectory/po/*-local.po and puts the resulting
      .mo file in AddonDirectory/locale/*/LC_MESSAGES/addon.mo

   python make.py dist-clean
   python make.py dist-clean AddonDirectory
   python make.py clean
   python make.py clean AddonDirectory
"""

import glob
import sys
import os

if "GRAMPSPATH" in os.environ:
    GRAMPSPATH = os.environ["GRAMPSPATH"]
else:
    GRAMPSPATH = "../../.."

if not os.path.isdir(GRAMPSPATH + "/po"):
    raise ValueError("Where is GRAMPSPATH/po: '%s/po'? Use 'GRAMPSPATH=path python make.py ...'" % GRAMPSPATH)

command = sys.argv[1]
if len(sys.argv) >= 3:
    addon = sys.argv[2]

def system(scmd, **kwargs):
    """
    Replace and call system with scmd.
    """
    cmd = r(scmd, **kwargs)
    print cmd
    os.system(cmd)

def echo(scmd, **kwargs):
    """
    Replace and echo.
    """
    cmd = r(scmd, **kwargs)
    print cmd

def r(scmd, **kwargs):
    """
    Replace scmd with variables from kwargs, or globals.
    """
    keywords = globals()
    keywords.update(kwargs)
    cmd = scmd % keywords
    return cmd

def increment_target(filenames):
    for filename in filenames:
        print filename
        fp = open(filename, "r")
        newfp = open("%s.new" % filename, "w")
        for line in fp:
            if (("gramps_target_version" in line) and 
                ("=" in line) and 
                (not line.strip().startswith('#'))):
                print "orig =", line.rstrip()
                line, stuff = line.rsplit(",", 1)
                line = line.rstrip()
                pos = line.index("gramps_target_version")
                indent = line[0:pos]
                var, gtv = line[pos:].split('=', 1)
                lyst = version(gtv.strip()[1:-1])
                lyst[2] += 1
                newv = ".".join(map(str, lyst))
                newline = "%sgramps_target_version = '%s',\n" % (indent, newv)
                newfp.write(newline)
            else:
                newfp.write(line)
        fp.close()
        newfp.close()
        system('''mv -f "%(file1)s" "%(file2)s" ''',
               file1="%s.new" % filename, file2=filename)


def myint(s):
    """
    Protected version of int()
    """
    try:
        v = int(s)
    except:
        v = s
    return v

def version(sversion):
    """
    Return the tuple version of a string version.
    """
    return [myint(x or "0") for x in (sversion + "..").split(".")][0:3]

if command == "clean":
    if len(sys.argv) == 2:
        for addon in [name for name in os.listdir(".") 
                      if os.path.isdir(name) and not name.startswith(".")]:
            system('''rm -rf -v '''
                   '''"%(addon)s"/*~ '''
                   '''"%(addon)s"/po/*~ '''
                   '''"%(addon)s"/po/template.pot '''
                   '''"%(addon)s"/po/*-global.po '''
                   '''"%(addon)s"/po/*-temp.po '''
                   '''"%(addon)s"/locale '''
                   '''"%(addon)s"/*.pyc '''
                   '''"%(addon)s"/*.pyo ''')
    else:
        system('''rm -rf -v '''
               '''"%(addon)s"/*~ '''
               '''"%(addon)s"/po/*~ '''
               '''"%(addon)s"/po/template.pot '''
               '''"%(addon)s"/po/*-global.po '''
               '''"%(addon)s"/po/*-temp.po '''
               '''"%(addon)s"/locale '''
               '''"%(addon)s"/*.pyc '''
               '''"%(addon)s"/*.pyo ''')
elif command == "init":
    # # Get all of the strings from the addon and create template.po:
    # #intltool-extract --type=gettext/glade *.glade
    if len(sys.argv) == 3:
        system('''mkdir -p "%(addon)s/po"''')
        system('''mkdir -p "%(addon)s/locale"''')
        system('''intltool-extract --type=gettext/glade "%(addon)s"/*.glade''')
        system('''intltool-extract --type=gettext/xml "%(addon)s"/*.xml''')
        system('''xgettext --language=Python --keyword=_ --keyword=N_'''
               ''' -o "%(addon)s/po/template.pot" "%(addon)s"/*.py ''')
        system('''xgettext -j --keyword=_ --keyword=N_'''
               ''' -o "%(addon)s/po/template.pot" '''
               '''"%(addon)s"/*.glade.h''')
        system('''xgettext -j --keyword=_ --keyword=N_'''
               ''' -o "%(addon)s/po/template.pot" '''
               '''"%(addon)s"/*.xml.h''')
        system('''sed -i 's/charset=CHARSET/charset=UTF-8/' '''
               '''"%(addon)s/po/template.pot"''')
    elif len(sys.argv) > 3:
        locale = sys.argv[3]
        # make a copy for locale
        if os.path.isfile(r('''%(addon)s/po/%(locale)s-local.po''')):
            raise ValueError(r('''%(addon)s/po/%(locale)s-local.po''') + 
                             " already exists!")
        system('''msginit --locale=%(locale)s ''' 
               '''--input="%(addon)s/po/template.pot" '''
               '''--output="%(addon)s/po/%(locale)s-local.po"''')
        echo('''You can now edit "%(addon)s/po/%(locale)s-local.po"''')
    else:
        raise AttributeError("init what?")
elif command == "update":
    locale = sys.argv[3]
    # Update the template file:
    if not os.path.isfile(r('''%(addon)s/po/template.pot''')):
        raise ValueError(r('''%(addon)s/po/template.pot'''
                           ''' is missing!\n  run '''
                           '''./make.py init %(addon)s'''))
    # #intltool-extract --type=gettext/glade *.glade
    system('''intltool-extract --type=gettext/glade "%(addon)s"/*.glade''')
    system('''intltool-extract --type=gettext/xml "%(addon)s"/*.xml''')
    system('''xgettext -j --language=Python --keyword=_ --keyword=N_'''
           ''' -o "%(addon)s/po/template.pot" "%(addon)s"/*.py ''')
    system('''xgettext -j --language=Python --keyword=_ --keyword=N_'''
           ''' -o "%(addon)s/po/template.pot" "%(addon)s"/*.glade.h''')
    system('''xgettext -j --language=Python --keyword=_ --keyword=N_'''
           ''' -o "%(addon)s/po/template.pot" "%(addon)s"/*.xml.h''')
    # Start with Gramps main PO file:
    locale_po_files = [r("%(GRAMPSPATH)s/po/%(locale)s.po")]
    # Next, get all of the translations from other addons:
    for module in [name for name in os.listdir(".") if os.path.isdir(name)]:
        # skip the addon we are updating:
        if module == addon:
            continue
        po_file = r("%(module)s/po/%(locale)s-local.po", module=module)
        if os.path.isfile(po_file):
            locale_po_files.append(po_file)
    # Concat those together:
    system('''msgcat --use-first %(list)s '''
           '''-o "%(addon)s/po/%(locale)s-global.po"''', 
           list=" ".join(['''"%s"''' % name for name in locale_po_files]))
    # Merge the local and global:
    #locale_local = r("%(module)s/po/%(locale)s-local.po", module=module)
    #if os.path.isfile(locale_local):
    system('''msgmerge -U "%(addon)s/po/%(locale)s-global.po" '''
           '''"%(addon)s/po/%(locale)s-local.po" ''')
    # Get all of the addon strings out of the catalog:
    system('''msggrep --location=%(addon)s/* '''
           '''"%(addon)s/po/%(locale)s-global.po" '''
           '''--output-file="%(addon)s/po/%(locale)s-temp.po"''')
    # Finally, add back any updates to the local version:
    system('''msgcat --use-first '''
           '''"%(addon)s/po/%(locale)s-temp.po" '''
           '''"%(addon)s/po/%(locale)s-local.po" '''
           '''-o "%(addon)s/po/%(locale)s-local.po.2" ''')
    system('''cp "%(addon)s/po/%(locale)s-local.po" '''
           '''"%(addon)s/po/%(locale)s-local.po.1" ''')
    system('''cp "%(addon)s/po/%(locale)s-local.po.2" '''
           '''"%(addon)s/po/%(locale)s-local.po" ''')
    system('''rm -v "%(addon)s/po/%(locale)s-local.po.1" '''
           '''"%(addon)s/po/%(locale)s-local.po.2" ''')
    # # Done!
    echo('''\nYou can edit "%(addon)s/po/%(locale)s-local.po"''')
elif command in ["compile"]:
    if addon == "all":
        dirs = [file for file in glob.glob("*") if os.path.isdir(file)]
        for addon in dirs:
            for po in glob.glob(r('''%(addon)s/po/*.po''')):
                length= len(po)
                locale = po[length-11:length-9]
                system('''mkdir -p "%(addon)s/locale/%(locale)s/LC_MESSAGES/"''')
                system('''msgfmt %(po)s '''
                       '''-o "%(addon)s/locale/%(locale)s/LC_MESSAGES/addon.mo"''')
    else:
        for po in glob.glob(r('''%(addon)s/po/*.po''')):
            length= len(po)
            locale = po[length-11:length-9]
            system('''mkdir -p "%(addon)s/locale/%(locale)s/LC_MESSAGES/"''')
            system('''msgfmt %(po)s '''
                   '''-o "%(addon)s/locale/%(locale)s/LC_MESSAGES/addon.mo"''')
elif command == "build":
    files = sys.argv[3:]
    if addon == "all":
        dirs = [file for file in glob.glob("*") if os.path.isdir(file)]
        # Compile all:
        for addon in dirs:
            for po in glob.glob(r('''%(addon)s/po/*.po''')):
                length= len(po)
                locale = po[length-11:length-9]
                system('''mkdir -p "%(addon)s/locale/%(locale)s/LC_MESSAGES/"''')
                system('''msgfmt %(po)s '''
                       '''-o "%(addon)s/locale/%(locale)s/LC_MESSAGES/addon.mo"''')
        # Build all:
        for addon in dirs:
            files = []
            files += glob.glob(r('''%(addon)s/*.py'''))
            files += glob.glob(r('''%(addon)s/*.glade'''))
            files += glob.glob(r('''%(addon)s/*.xml'''))
            files += glob.glob(r('''%(addon)s/locale/*/LC_MESSAGES/*.mo'''))
            files_str = " ".join(files)
            system('''mkdir -p ../download ''')
            increment_target(glob.glob(r('''%(addon)s/*gpr.py''')))
            system('''tar cfz "../download/%(addon)s.addon.tgz" %(files)s''',
                   files=files_str)
    else:
        files += glob.glob(r('''%(addon)s/*.py'''))
        files += glob.glob(r('''%(addon)s/*.glade'''))
        files += glob.glob(r('''%(addon)s/*.xml'''))
        files += glob.glob(r('''%(addon)s/locale/*/LC_MESSAGES/*.mo'''))
        files_str = " ".join(files)
        system('''mkdir -p ../download ''')
        increment_target(glob.glob(r('''%(addon)s/*gpr.py''')))
        system('''tar cfz "../download/%(addon)s.addon.tgz" %(files)s''',
               files=files_str)
else:
    raise AttributeError("unknown command")
