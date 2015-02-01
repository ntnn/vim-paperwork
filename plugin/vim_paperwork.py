from paperworks import models

from view import *
from util import *

import vim

version = "0.1a1"

host = vim.eval('g:PaperworkHost')
user = vim.eval('g:PaperworkUser')
passwd = vim.eval('g:PaperworkPassword')

default_indent = vim.eval('g:PaperworkDefaultIndent')


class PaperworkVim:
    def __init__(self):
        self.pw = models.Paperwork(user, passwd, host)
        self.pw.download()
        self.pwbuffers = PaperworkBuffers(self.pw, version)
        self.tabs = {}
        self.currTabId = 0

    def open(self):
        """Open a sidebar."""
        try:
            self.tabs[util.get_tab_id()].open_sidebar()
        except:
            self.tabs[self.currTabId] = PaperworkTab(self.pwbuffers)
            util.set_tab_id(self.currTabId)
            self.currTabId += 1

    def sync(self):
        """Sync the local paperwork session with the remote host."""
        self.pw.update()
        self.pwbuffers.update_buffers()
        self.pwbuffers.print_sidebar()

    def parse_sidebar(self):
        self.pwbuffers.parse_sidebar_buffer()

    def open_note(self):
        """Opens a note."""
        line = vim.current.line
        if line[0] in default_indent:
            note = self.pw.find_note(util.parse_title(line))
            self.tabs[util.get_tab_id()].open_note(note)

    def write_note(self):
        """Autocmd hook to update a note."""
        note = self.pw.find_note(util.get_note_id())
        self.pwbuffers.write_note_buffer(note)

    def close_note(self):
        """Autocmd hook to delete the temporary file."""
        note = self.pw.find_note(util.get_note_id())
        self.pwbuffers.delete_note_buffer(note)
