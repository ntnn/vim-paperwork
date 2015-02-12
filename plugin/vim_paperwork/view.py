"""
This file holds the buffer and window logic.

PaperworkBuffers holds all buffers and their referring methods -
creating, deleting, updating.

PaperworkTab holds only the methods for managing windows and
placing the right buffers in them.

"""

from util import *
import logging

LOGGER = logging.getLogger(__name__)

NOTE_WINDOW_CMDS = {
    'bottom': 'botright new',
    'top': 'topleft new',
    'right': 'vertical botright new',
    'left': 'vertical topleft new'
    }


class PaperworkBuffers:
    """Class representing the vim_paperwork buffers."""
    def __init__(self, pw, version):
        """Initializes the class but no values.

        :type pw: Paperwork
        :type version: int
        """
        self.sidebarbuffer = None
        self.last_sidebarbuffer = None
        self.last_deleted = []
        self.notebuffers = {}
        self.tempfiles = {}
        self.pw = pw
        self.version = version
        LOGGER.info('Initialized PaperworkBuffers')

    def print_sidebar(self):
        """Replaces sidebar buffer with new assembled information."""
        LOGGER.info('Printing sidebar')
        ret = ['+++ vim-paperwork v{} +++'.format(self.version),
               '', "+++ Notebooks +++"]
        for nb in self.pw.get_notebooks():
            ret.extend(coll_to_list(nb))
        ret += ['+++ Tags +++']
        for tag in self.pw.get_tags():
            ret.extend(coll_to_list(tag))
        self.sidebarbuffer[:] = ret
        self.last_sidebarbuffer = ret

    def create_sidebar_buffer(self):
        """Creates sidebar buffer and initializes with correct settings."""
        LOGGER.info('Creating sidebarbuffer')
        bufferfile = get_tempfile('sidebar')
        cmd('edit {}'.format(bufferfile.name))
        self.sidebarbuffer = vim.current.buffer
        set_folding()
        cmd('nnoremap <silent> <buffer> <CR> :call PaperworkOpenNote()<CR>')  # noqa
        cmd('autocmd TextChanged,InsertLeave <buffer> call PaperworkSidebarChanged()')  # noqa
        cmd('autocmd BufWrite <buffer> call PaperworkSync()')
        LOGGER.info('Created sidebarbuffer')

    def parse_sidebar_buffer(self):
        """Autocmd hook to apply changes."""
        LOGGER.info('Parsing sidebarbuffer')
        old_buffer = set(self.last_sidebarbuffer)
        new_buffer = set(self.sidebarbuffer[:])
        len_old_buffer = len(old_buffer)
        len_new_buffer = len(new_buffer)

        if len_new_buffer > len_old_buffer:
            self.add_entries(
                [entry
                 for entry in self.sidebarbuffer[:]
                 if entry not in old_buffer])
        elif len_new_buffer < len_old_buffer:
            self.remove_entries(
                [entry
                 for entry in old_buffer
                 if entry not in new_buffer])
        else:
            self.change_entries(
                [linenumber
                 for linenumber, title in enumerate(self.sidebarbuffer[:])
                 if title not in old_buffer])
        LOGGER.info('Finished parsing sidebarbuffer, printing')
        self.print_sidebar()

    def add_entries(self, new_entries):
        """Parses new entries to the paperwork instance.

        :type new_entries: list
        """
        LOGGER.info('Parsing new entries to paperwork')
        # Find notebook to add to
        index = self.sidebarbuffer[:].index(new_entries[0]) - 1
        LOGGER.info('Finding notebook')
        while (self.sidebarbuffer[index] == '' or
               self.sidebarbuffer[index][0] in SETTINGS['PaperworkDefaultIndent']):
            index -= 1
        LOGGER.info('Searching for notebook in paperwork')
        notebook = self.pw.find_notebook(
            parse_title(
                self.sidebarbuffer[index]))

        LOGGER.info('Parsing entries')
        for entry in new_entries:
            LOGGER.info('Entry: {}'.format(entry))
            title = parse_title(entry)
            if entry[0] not in SETTINGS['PaperworkDefaultIndent']:
                LOGGER.info('Found notebook entry, creating notebook')
                # create notebook if no indentation is present
                # TODO (Nelo Wallus): add tag creation
                notebook = self.pw.create_notebook(entry)
            else:
                note = None
                # Check for deleted items first
                for deleted in self.last_deleted:
                    LOGGER.info('Searching deleted notes')
                    if title == deleted.title:
                        note = deleted
                        self.last_deleted.remove(note)
                        break
                if not note:
                    LOGGER.info('Finding note in paperwork')
                    note = self.pw.find_note(title)
                if note:
                    LOGGER.info('Found existing note, moving {} to {}'.format(
                        note, note.notebook))
                    note.move_to(notebook)
                else:
                    LOGGER.info('New note, creating note in notebook')
                    notebook.create_note(title)

    def remove_entries(self, old_entries):
        """Removed old entries from the paperwork instance.

        :type old_entries: list
        """
        LOGGER.info('Parsing old entries to remove')
        # Delete previously saved entries
        LOGGER.info('Deleting previous deleted entries')
        for entry in self.last_deleted:
            entry.delete()
        self.last_deleted = []

        for entry in old_entries:
            LOGGER.info('Parsing entry {}'.format(entry))
            title = parse_title(entry)
            entry = self.pw.find_note(title)
            if entry:
                LOGGER.info('Found note {}, adding to last deleted'.format(
                    entry))
                # Notes are saved in case of pasting into
                # another notebook
                del(entry.notebook.notes[entry.id])
                self.last_deleted.append(entry)
            else:
                # Notebooks are deleted immediately
                entry = self.pw.find_notebook(title)
                if entry:
                    LOGGER.info('Found notebook {}, deleting'.format(entry))
                    self.pw.delete_notebook(entry)
                else:
                    LOGGER.info('Entry not found: {}'.format(entry))
                # TODO (Nelo Wallus): Add tag deletion

    def change_entries(self, changed_lines):
        """Apply changes in titles in paperwork instance.

        :type changed_lines: list
        """
        LOGGER.info('Parsing changed entries')
        for linenumber in changed_lines:
            old_title = parse_title(self.last_sidebarbuffer[linenumber])
            new_title = parse_title(self.sidebarbuffer[linenumber])
            entry = self.pw.find_note(old_title)
            if not entry:
                entry = self.pw.find_notebook(old_title)
            # TODO (Nelo Wallus): Add tag
            LOGGER.info('Changed {} title to {}'.format(entry, new_title))
            entry.title = new_title
            entry.update()

    def open_note_buffer(self, note):
        """Creates temporary file and opens it.

        :type note: Note
        """
        LOGGER.info('Opening notebuffer for {}'.format(note))
        if note.id in self.notebuffers:
            LOGGER.info('Notebuffer exists, switching')
            vim.current.buffer = self.notebuffers[note.id]
        else:
            tempfile = get_tempfile(note.title)
            LOGGER.info('Created tempfile {}'.format(tempfile.name))
            cmd('edit {}'.format(tempfile.name))
            vim.current.buffer[:] = note.content.splitlines()
            cmd('write!')
            self.notebuffers[note.id] = vim.current.buffer
            self.tempfiles[note.id] = tempfile
            set_note_id(note.id)
            cmd('autocmd BufWrite <buffer> call PaperworkNoteBufferWrite()')
            cmd('autocmd BufDelete <buffer> call PaperworkNoteBufferDelete()')
            LOGGER.info('Opened notebuffer')

    def write_note_buffer(self, note):
        """Autocmd hook to write current buffer to note and update on host.

        :type note: Note
        """
        LOGGER.info('Writing buffer to note {}'.format(note))
        note.content = '\n'.join(vim.current.buffer[:])
        note.update(force=True)
        LOGGER.info('Wrote buffer')

    def delete_note_buffer(self, note):
        """Autocmd hook to delete temporary file.

        :type note: Note
        """
        LOGGER.info('Closing buffer for note {}'.format(note))
        self.tempfiles[note.id].close()

    def update_buffers(self):
        """Overwrite all opened note buffers with updated content from host."""
        LOGGER.info('Updating open buffers')
        for note_id in self.notebuffers:
            LOGGER.info('Updating buffer for note with id {}'.format(note_id))
            self.notebuffers[note_id][:] = self.pw.find_note(
                note_id).content.splitlines()
        self.print_sidebar()
        LOGGER.info('Finished updating open buffers')


class PaperworkTab:
    """Class representing vim tabs."""
    def __init__(self, pwbuffers):
        """Initializes the class and the current vim tab.

        :param PaperworkBuffers pwbuffers: Instance of PaperworkBuffers to fill
            the windows with correct buffers.
        """
        self.pwbuffers = pwbuffers
        self.sidebarwindow = None
        self.notebarwindow = None
        self.current_notebook = None
        self.notewindow = None
        self.open_sidebar()
        LOGGER.info('Initialized PaperworkTab')

    def open_sidebar(self):
        """Opens sidebar or creates a new one if not present."""
        LOGGER.info('Opening sidebar window')
        self.notewindow = vim.current.window
        try:
            vim.current.window = self.sidebarwindow
        except:
            self.create_sidebar_window()
        if not self.pwbuffers.sidebarbuffer:
            self.pwbuffers.create_sidebar_buffer()
        else:
            vim.current.buffer = self.pwbuffers.sidebarbuffer
        LOGGER.info('Opened sidebar window, printing sidebar buffer')
        self.pwbuffers.print_sidebar()

    def create_sidebar_window(self):
        """Creates sidebar window."""
        LOGGER.info('Creating sidebar window')
        cmd('vertical topleft {}new'.format(SETTINGS['PaperworkDefaultWidth']))
        self.sidebarwindow = vim.current.window
        LOGGER.info('Created sidebar window')

    def open_note(self, note):
        """Enter-hook to open note under cursor."""
        LOGGER.info('Opening note window')
        default_note_window = SETTINGS['PaperworkDefaultNoteWindow']
        if default_note_window in NOTE_WINDOW_CMDS:
            cmd(NOTE_WINDOW_CMDS[default_note_window])
        else:
            try:
                vim.current.window = self.notewindow
            except:
                cmd('vsplit new')
                vim.current.window = self.notewindow
        self.pwbuffers.open_note_buffer(note)
        LOGGER.info('Opened note window')
