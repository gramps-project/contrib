#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2006-2007  Alex Roitman
# Copyright (C) 2008-2009  Gary Burton
# Copyright (C) 2007-2009  Jerome Rapinat
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
Display Sources related to repositories
"""

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------

from gen.plug.menu import BooleanOption
from ReportBase import Report, ReportUtils, MenuReportOptions
from TransUtils import get_addon_translator
from gen.plug.docgen import (IndexMark, FontStyle, ParagraphStyle, 
                             FONT_SANS_SERIF, FONT_SERIF, 
                             INDEX_TYPE_TOC, PARA_ALIGN_CENTER)

_ = get_addon_translator(__file__).gettext

class RepositoryReportAlt(Report):
    """
    Repository Report class
    """
    def __init__(self, database, options_class):
        """
        Create the RepositoryReport object produces the Repositories report.
        
        The arguments are:

        database        - the GRAMPS database instance
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.

        incintern    - Whether to include urls for repository.
        incaddres    - Whether to include addresses for repository.
        incauthor    - Whether to include author of source.
        incabbrev    - Whether to include abbreviation of source.
        incpublic    - Whether to include publication information of source.
        incdatamp    - Whether to include data keys and values of source.
        inclunote    - Whether to include notes of source or repository.
        inclmedia    - Whether to include media of source.
        incprivat    - Whether to include private records.

        """

        Report.__init__(self, database, options_class)

        menu = options_class.menu
        self.inc_intern = menu.get_option_by_name('incintern').get_value()
        self.inc_addres = menu.get_option_by_name('incaddres').get_value()
        self.inc_author = menu.get_option_by_name('incauthor').get_value()
        self.inc_abbrev = menu.get_option_by_name('incabbrev').get_value()
        self.inc_public = menu.get_option_by_name('incpublic').get_value()
        self.inc_datamp = menu.get_option_by_name('incdatamp').get_value()
        self.inclu_note = menu.get_option_by_name('inclunote').get_value()
        self.incl_media = menu.get_option_by_name('inclmedia').get_value()
        self.inc_privat = menu.get_option_by_name('incprivat').get_value()

    def write_report(self):
        """
        The routine the actually creates the report. At this point, the document
        is opened and ready for writing.
        """

        # Write the title line. Set in INDEX marker so that this section will be
        # identified as a major category if this is included in a Book report.

        title = _('Repositories Report')
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.start_paragraph('REPO-ReportTitle')
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()
        self.__write_all_repositories()
        
    def __write_all_repositories(self):
        """
        This procedure writes out all repositories.
        """

        rlist = self.database.get_repository_handles()
        for handle in rlist:
            self.__write_repository(handle)
            self.__write_referenced_sources(handle)

    def __write_repository(self, handle):
        """
        This procedure writes out the details of a single repository.
        """

        repository = self.database.get_repository_from_handle(handle)

        self.doc.start_paragraph('REPO-RepositoryTitle')

        # ignore private record

        if not self.inc_privat and repository.private:
            self.doc.write_text(_('Private'))
        else:
            self.doc.write_text(('%(repository)s (%(type)s)') % 
                                {'repository' : repository.get_name(),
                                'type' : repository.get_type()})
        self.doc.end_paragraph()

        # display notes and allows markups

        if repository.get_referenced_handles() and self.inclu_note:
            notelist = repository.get_referenced_handles()
            for note_handle in notelist:

            # ignore private records

                if not self.inc_privat and repository.private:
                    pass
                else:

                    # on tuple : [0] = classname ; [1] = handle

                    note_handle = note_handle[1] 
                    self.__write_referenced_notes(note_handle)

        # additional repository informations

        child_list = repository.get_text_data_child_list()
        addresses = repository.get_handle_referents()
        for address_handle in addresses:
            address = ReportUtils.get_address_str(address_handle)

            if self.inc_intern or self.inc_addres:
                self.doc.start_paragraph('REPO-Section2')

                # ignore private records

                if not self.inc_privat and (repository.private):
                    pass
                else:
                    #if self.inc_intern:
                        #self.doc.write_text(_('Internet: %s') % internet)
                    if self.inc_addres:
                        self.doc.write_text(_('\nAddress: %s') % address)
                self.doc.end_paragraph()

    def __write_referenced_sources(self, handle):
        """
        This procedure writes out each of the sources related to the repository.
        """

        repository = self.database.get_repository_from_handle(handle)
        repository_handles = [handle for (object_type, handle) in \
                         self.database.find_backlink_handles(handle,['Source'])]

        source_nbr = 0

        for source_handle in repository_handles:
            src = self.database.get_source_from_handle(source_handle)

            # Get the list of references from this source to our repo
            # (can be more than one, technically)

            for reporef in src.get_reporef_list():
                if reporef.ref == repository.handle:
                    source_nbr += 1
                    self.doc.start_paragraph('REPO-Section')

                    # ignore private records

                    if not self.inc_privat and (src.private or repository.private):
                        title = _('%s. Private') % source_nbr
                    else:
                        title = (('%(nbr)s. %(name)s (%(type)s) : %(call)s') % 
                                    {'nbr' : source_nbr,
                                     'name' : src.get_title(),
                                     'type' : str(reporef.get_media_type()),
                                     'call' : reporef.get_call_number()})
                    self.doc.write_text(title)
                    self.doc.end_paragraph()

                    # additional source informations

                    author = src.get_author()
                    abbrev = src.get_abbreviation()
                    public = src.get_publication_info()

                    # keys and values into a dict {}

                    keyval = src.get_data_map()

                    # list of tuples [('',''),('','')]

                    listup = keyval.items()

                    # format strings

                    dictio = ['%s=%s' % (k, v) for k, v in listup]

                    # one string and '; ' as separator

                    data = '; '.join(dictio)

                    # if need, generates child section

                    if self.inc_author or self.inc_abbrev or self.inc_public or self.inc_datamp:
                        self.doc.start_paragraph('REPO-Section2')
                        if not self.inc_privat and (src.private or repository.private):
                            pass
                        else:
                            if self.inc_author:
                                self.doc.write_text(_('Author: %s') % author)
                            if self.inc_abbrev:
                                self.doc.write_text(_('\nAbbreviation: %s') % abbrev)
                            if self.inc_public:
                                self.doc.write_text(_('\nPublication information: %s') % public)
                            if self.inc_datamp:
                                self.doc.write_text(_('\nData: %s') % data)
                        self.doc.end_paragraph()

                    # display notes and allows markups

                    if src.get_referenced_handles() and self.inclu_note:
                        notelist = src.get_referenced_handles()
                        for note_handle in notelist:

                            # ignore private records

                            if not self.inc_privat and (src.private or repository.private):
                                pass
                            else:

                                # on tuple : [0] = classname ; [1] = handle

                                note_handle = note_handle[1] 
                                self.__write_referenced_notes(note_handle)

                    if src.get_sourcref_child_list() and self.incl_media:
                        medialist = src.get_sourcref_child_list()
                        for media_handle in medialist:

                            # ignore private records

                            if not self.inc_privat and (src.private or repository.private):
                                pass
                            else:
                                photo = src.get_media_list()
                                self.__write_referenced_media(photo, media_handle)

    def __write_referenced_notes(self, note_handle):
        """
        This procedure writes out each of the notes related to the repository or source.
        """

        note = self.database.get_note_from_handle(note_handle)

        # ignore private records

        if not self.inc_privat and note.private:
            pass
        else:
            self.doc.write_styled_note(note.get_styledtext(),
                                           note.get_format(), 'REPO-Note')

    def __write_referenced_media(self, photo, media_handle):
        """
        This procedure writes out each of the media related to the source.
        """

        photo = photo[0]

        # ignore private records

        if not self.inc_privat and media_handle.private:
            pass
        else:
            
            #self.doc.add_media_object(name=filename, align=right, w_cm=4, h_cm=4)

            ReportUtils.insert_image(self.database, self.doc, photo)

#------------------------------------------------------------------------
#
# RepositoryOptions
#
#------------------------------------------------------------------------

class RepositoryOptionsAlt(MenuReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        """
        Add options to the menu for the place report.
        """

        category_name = _('Report Options')

        incintern = BooleanOption(_("Include repository's urls"), False)
        incintern.set_help(_('Whether to include urls on repository.'))
        menu.add_option(category_name, 'incintern', incintern)

        incaddres = BooleanOption(_("Include repository's address"), False)
        incaddres.set_help(_('Whether to include addresses on repository.'))
        menu.add_option(category_name, 'incaddres', incaddres)

        incauthor = BooleanOption(_("Include source's author"), False)
        incauthor.set_help(_('Whether to include author.'))
        menu.add_option(category_name, 'incauthor', incauthor)

        incabbrev = BooleanOption(_("Include source's abbreviation"), False)
        incabbrev.set_help(_('Whether to include abbreviation.'))
        menu.add_option(category_name, 'incabbrev', incabbrev)

        incpublic = BooleanOption(_("Include source's publication information"), False)
        incpublic.set_help(_('Whether to include publication information.'))
        menu.add_option(category_name, 'incpublic', incpublic)

        incdatamp = BooleanOption(_("Include source's data"), False)
        incdatamp.set_help(_('Whether to include keys and values.'))
        menu.add_option(category_name, 'incdatamp', incdatamp)

        inclunote = BooleanOption(_('Include notes'), False)
        inclunote.set_help(_('Whether to include notes on repositories and sources.'))
        menu.add_option(category_name, 'inclunote', inclunote)

        inclmedia = BooleanOption(_('Include media'), False)
        inclmedia.set_help(_('Whether to include media on sources.'))
        menu.add_option(category_name, 'inclmedia', inclmedia)

        incprivat = BooleanOption(_('Include private records'), False)
        incprivat.set_help(_('Whether to include repositories and sources marked as private.'))
        menu.add_option(category_name, 'incprivat', incprivat)

    def make_default_style(self, default_style):
        """
        Make the default output style for the report.
        """

        self.default_style = default_style
        self.__report_title_style()
        self.__repository_title_style()
        self.__section_style()
        self.__child_section_style()
        self.__note_style()

    def __report_title_style(self):
        """
        Define the style used for the report title
        """

        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=20, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_bottom_border(1)
        para.set_top_margin(ReportUtils.pt2cm(20))
        para.set_bottom_margin(ReportUtils.pt2cm(20))
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the title of the report.'))
        self.default_style.add_paragraph_style('REPO-ReportTitle', para)

    def __repository_title_style(self):
        """
        Define the style used for the repository title
        """

        font = FontStyle()
        font.set(face=FONT_SERIF, size=14, italic=0, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_top_margin(ReportUtils.pt2cm(10))
        para.set_bottom_margin(ReportUtils.pt2cm(7))
        para.set_description(_('The style used for repository title.'))
        self.default_style.add_paragraph_style('REPO-RepositoryTitle', para)

    def __section_style(self):
        """
        Define the style used for primary section
        """

        font = FontStyle()
        font.set(face=FONT_SERIF, size=10, italic=0, bold=0)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=0, lmargin=0.5)
        para.set_top_margin(ReportUtils.pt2cm(7))
        para.set_bottom_margin(ReportUtils.pt2cm(5))
        para.set_description(_('The style used for each section.'))
        self.default_style.add_paragraph_style('REPO-Section', para)

    def __child_section_style(self):
        """
        Define the style used for secondary section
        """

        font = FontStyle()
        font.set(face=FONT_SERIF, size=10, italic=1, bold=0)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=0, lmargin=1)
        para.set_top_margin(ReportUtils.pt2cm(1))
        para.set_bottom_margin(ReportUtils.pt2cm(1))
        para.set_description(_('The style used for child section.'))
        self.default_style.add_paragraph_style('REPO-Section2', para)

    def __note_style(self):
        """
        Define the style used for note
        """

        para = ParagraphStyle()
        para.set(first_indent=-0.75, lmargin=.75)
        para.set_top_margin(ReportUtils.pt2cm(3))
        para.set_bottom_margin(ReportUtils.pt2cm(3))
        para.set_description(_('The basic style used for the note display.'))
        self.default_style.add_paragraph_style("REPO-Note", para)

