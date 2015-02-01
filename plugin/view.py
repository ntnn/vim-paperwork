import vim
import util
import logging
logger = logging.getLogger(__name__)

default_indent = vim.eval('g:PaperworkDefaultIndent')
default_width = vim.eval('g:PaperworkDefaultWidth')
default_notebook = vim.eval('g:PaperworkDefaultNotebook')
default_note_window = vim.eval('g:PaperworkDefaultNoteWindow')

note_window_cmds = {
    'bottom': 'botright new',
    'top': 'topleft new',
    'right': 'vertical botright new',
    'left': 'vertical topleft new'
    }

"""
This file holds the buffer and window logic.

PaperworkBuffers holds all buffers and their referring methods -
creating, deleting, updating.

PaperworkTab holds only the methods for managing windows and
placing the right buffers in them.

"""


class PaperworkBuffers:
    def __init__(self, pw, version):
        self.sidebarbuffer = None
        self.last_sidebarbuffer = None
        self.last_deleted = []
        self.notebuffers = {}
        self.tempfiles = {}
        self.pw = pw
        self.version = version
        logger.info('Initialized PaperworkBuffers')

    def print_sidebar(self):
        """Replaces sidebar buffer with new assembled information."""
        logger.info('Printing sidebar')
        ret = ['+++ vim-paperwork v{} +++'.format(self.version),
               '', "+++ Notebooks +++"]
        for nb in self.pw.get_notebooks():
            ret.extend(util.coll_to_list(nb))
        ret += ['+++ Tags +++']
        for tag in self.pw.get_tags():
            ret.extend(util.coll_to_list(tag))
        self.sidebarbuffer[:] = ret
        self.last_sidebarbuffer = ret

    def create_sidebar_buffer(self):
        """Creates sidebar buffer and initializes with correct settings."""
        logger.info('Creating sidebarbuffer')
        bufferfile = util.get_tempfile('sidebar')
        vim.command('edit {}'.format(bufferfile.name))
        self.sidebarbuffer = vim.current.buffer
        util.set_folding()
        vim.command('nnoremap <silent> <buffer> <CR> :call PaperworkOpenNote()<CR>')  # noqa
        vim.command('autocmd TextChanged,InsertLeave <buffer> call PaperworkSidebarChanged()')  # noqa
        vim.command('autocmd BufWrite <buffer> call PaperworkSync()')
        logger.info('Created sidebarbuffer')

    def parse_sidebar_buffer(self):
        """Autocmd hook to apply changes."""
        logger.info('Parsing sidebarbuffer')
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
        logger.info('Finished parsing sidebarbuffer, printing')
        self.print_sidebar()

    def add_entries(self, new_entries):
        logger.info('Parsing new entries to paperwork')
        # Find notebook to add to
        index = self.sidebarbuffer[:].index(new_entries[0]) - 1
        logger.info('Finding notebook')
        while (self.sidebarbuffer[index] == '' or
               self.sidebarbuffer[index][0] in default_indent):
            index -= 1
        logger.info('Searching for notebook in paperwork')
        notebook = self.pw.find_notebook(
            util.parse_title(
                self.sidebarbuffer[index]))

        logger.info('Parsing entries')
        for entry in new_entries:
            logger.info('Entry: {}'.format(entry))
            title = util.parse_title(entry)
            if entry[0] not in default_indent:
                logger.info('Found notebook entry, creating notebook')
                # create notebook if no indentation is present
                # TODO (Nelo Wallus): add tag creation
                notebook = self.pw.create_notebook(entry)
            else:
                note = None
                # Check for deleted items first
                for deleted in self.last_deleted:
                    logger.info('Searching deleted notes')
                    if title == deleted.title:
                        note = deleted
                        self.last_deleted.remove(note)
                        break
                if not note:
                    logger.info('Finding note in paperwork')
                    note = self.pw.find_note(title)
                if note:
                    logger.info('Found existing note, moving {} to {}'.format(
                        note, note.notebook))
                    note.move_to(notebook)
                else:
                    logger.info('New note, creating note in notebook')
                    notebook.create_note(title)

    def remove_entries(self, old_entries):
        logger.info('Parsing old entries to remove')
        # Delete previously saved entries
        logger.info('Deleting previous deleted entries')
        for entry in self.last_deleted:
            entry.delete()
        self.last_deleted = []

        for entry in old_entries:
            logger.info('Parsing entry {}'.format(entry))
            title = util.parse_title(entry)
            entry = self.pw.find_note(title)
            if entry:
                logger.info('Found note {}, adding to last deleted'.format(
                    entry))
                # Notes are saved in case of pasting into
                # another notebook
                del(entry.notebook.notes[entry.id])
                self.last_deleted.append(entry)
            else:
                # Notebooks are deleted immediately
                entry = self.pw.find_notebook(title)
                if entry:
                    logger.info('Found notebook {}, deleting'.format(entry))
                    entry.delete()
                else:
                    logger.info('Entry not found: {}'.format(entry))
                # TODO (Nelo Wallus): Add tag deletion

    def change_entries(self, changed_lines):
        logger.info('Parsing changed entries')
        for linenumber in changed_lines:
            old_title = util.parse_title(self.last_sidebarbuffer[linenumber])
            new_title = util.parse_title(self.sidebarbuffer[linenumber])
            entry = self.pw.find_note(old_title)
            if not entry:
                entry = self.pw.find_notebook(old_title)
            # TODO (Nelo Wallus): Add tag
            logger.info('Changed {} title to {}'.format(entry, new_title))
            entry.title = new_title
            entry.update()

    def open_note_buffer(self, note):
        """Creates temporary file and opens it."""
        logger.info('Opening notebuffer for {}'.format(note))
        if note.id in self.notebuffers:
            logger.info('Notebuffer exists, switching')
            vim.current.buffer = self.notebuffers[note.id]
        else:
            tempfile = util.get_tempfile(note.title)
            logger.info('Created tempfile {}'.format(tempfile.name))
            vim.command('edit {}'.format(tempfile.name))
            vim.current.buffer[:] = note.content.splitlines()
            vim.command('write!')
            self.notebuffers[note.id] = vim.current.buffer
            self.tempfiles[note.id] = tempfile
            util.set_note_id(note.id)
            vim.command('autocmd BufWrite <buffer> call PaperworkNoteBufferWrite()')  # noqa
            vim.command('autocmd BufDelete <buffer> call PaperworkNoteBufferDelete()')  # noqa
            logger.info('Opened notebuffer')

    def write_note_buffer(self, note):
        """Autocmd hook to write current buffer to note and update on host."""
        logger.info('Writing buffer to note {}'.format(note))
        note.content = '\n'.join(vim.current.buffer[:])
        note.update(force=True)
        logger.info('Wrote buffer')

    def delete_note_buffer(self, note):
        """Autocmd hook to delete temporary file."""
        logger.info('Closing buffer for note {}'.format(note))
        self.tempfiles[note.id].close()

    def update_buffers(self):
        """Overwrite all opened note buffers with updated content from host."""
        logger.info('Updating open buffers')
        for note_id in self.notebuffers:
            logger.info('Updating buffer for note with id {}'.format(note_id))
            self.notebuffers[note_id][:] = self.pw.find_note(
                note_id).content.splitlines()
        self.print_sidebar()
        logger.info('Finished updating open buffers')


class PaperworkTab:
    def __init__(self, pwbuffers):
        self.pwbuffers = pwbuffers
        self.sidebarwindow = None
        self.notebarwindow = None
        self.current_notebook = None
        self.notewindow = None
        self.open_sidebar()
        logger.info('Initialized PaperworkTab')

    def open_sidebar(self):
        """Opens sidebar or creates a new one if not present."""
        logger.info('Opening sidebar window')
        self.notewindow = vim.current.window
        try:
            vim.current.window = self.sidebarwindow
        except:
            self.create_sidebar_window()
        if not self.pwbuffers.sidebarbuffer:
            self.pwbuffers.create_sidebar_buffer()
        else:
            vim.current.buffer = self.pwbuffers.sidebarbuffer
        logger.info('Opened sidebar window, printing sidebar buffer')
        self.pwbuffers.print_sidebar()

    def create_sidebar_window(self):
        """Creates sidebar window."""
        logger.info('Creating sidebar window')
        vim.command('vertical topleft {}new'.format(default_width))
        self.sidebarwindow = vim.current.window
        logger.info('Created sidebar window')

    def open_note(self, note):
        """Enter-hook to open note under cursor."""
        logger.info('Opening note window')
        if default_note_window in note_window_cmds:
            vim.command(note_window_cmds[default_note_window])
        else:
            try:
                vim.current.window = self.notewindow
            except:
                vim.command('vsplit new')
                vim.current.window = self.notewindow
        self.pwbuffers.open_note_buffer(note)
        logger.info('Opened note window')
