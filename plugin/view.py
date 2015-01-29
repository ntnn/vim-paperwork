import vim
import os

import util

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
        self.notebuffers = {}
        self.tempfiles = {}
        self.pw = pw
        self.version = version

    def print_sidebar(self):
        """Replaces sidebar buffer with new assembled information."""
        # the plusses are really just for the expression
        ret = ['+++ vim-paperwork v{} +++'.format(self.version),
               '', "+++ Notebooks +++"]
        for nb in self.pw.get_notebooks():
            ret.extend(util.coll_to_list(nb))
        ret += ['+++ Tags +++']
        for tag in self.pw.get_tags():
            ret.extend(util.coll_to_list(tag))
        self.sidebarbuffer[:] = ret
        self.sidebarbuffer.name = 'vim-paperwork'

    def create_sidebar_buffer(self):
        """Creates sidebar buffer and initializes with correct settings."""
        vim.command('nnoremap <silent> <buffer> <CR> :call PaperworkOpenNote()<CR>')  # noqa
        self.sidebarbuffer = vim.current.buffer
        util.set_scratch()

    def open_note_buffer(self, note):
        """Creates temporary file and opens it."""
        tempfile = util.get_tempfile()
        vim.command('edit {}'.format(tempfile.name))
        vim.current.buffer[:] = note.content.splitlines()
        vim.command('write!')
        self.notebuffers[note.id] = vim.current.buffer
        self.tempfiles[note.id] = tempfile
        util.set_note_id(note.id)
        vim.command('autocmd BufWrite <buffer> call PaperworkNoteBufferWrite()')  # noqa
        vim.command('autocmd BufDelete <buffer> call PaperworkNoteBufferDelete()')  # noqa

    def write_note_buffer(self, note):
        """Autocmd hook to write current buffer to note and update on host."""
        note.content = '\n'.join(vim.current.buffer[:])
        note.update(force=True)

    def delete_note_buffer(self, note):
        """Autocmd hook to delete temporary file."""
        self.tempfiles[note.id].close()

    def update_buffers(self):
        """Overwrite all opened note buffers with updated content from host."""
        for note_id in self.notebuffers:
            self.notebuffers[note_id][:] = self.pw.find_note(
                note_id).content.splitlines()
        self.print_sidebar()


class PaperworkTab:
    def __init__(self, pwbuffers):
        self.pwbuffers = pwbuffers
        self.sidebarwindow = None
        self.notebarwindow = None
        self.current_notebook = None
        self.notewindow = None
        self.open_sidebar()

    def open_sidebar(self):
        """Opens sidebar or creates a new one if not present."""
        self.notewindow = vim.current.window
        try:
            vim.current.window = self.sidebarwindow
        except:
            self.create_sidebar_window()
        if not self.pwbuffers.sidebarbuffer:
            self.pwbuffers.create_sidebar_buffer()
        else:
            vim.current.buffer = self.pwbuffers.sidebarbuffer
        self.pwbuffers.print_sidebar()

    def create_sidebar_window(self):
        """Creates sidebar window."""
        vim.command('vertical topleft {}new'.format(default_width))
        self.sidebarwindow = vim.current.window

    def open_note(self, note):
        """Enter-hook to open note under cursor."""
        if default_note_window in note_window_cmds:
            vim.command(note_window_cmds[default_note_window])
        else:
            try:
                vim.current.window = self.notewindow
            except:
                vim.command('vsplit new')
                vim.current.window = self.notewindow
        self.pwbuffers.open_note_buffer(note)
