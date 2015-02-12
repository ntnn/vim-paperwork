from paperworks import models

import vim
import logging

from .util import *
from .view import *

if SETTINGS['PaperworkDebug'] == '1':
    handler = logging.FileHandler(
        'vim-paperwork.log', mode='w')
    handler.formatter = logging.Formatter(
        '%(asctime)s [%(levelname)-5s @ '
        '%(filename)-10s:%(funcName)-15s:%(lineno)-4s] '
        '%(process)-6s - %(message)s')
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)
LOGGER = logging.getLogger(__name__)

__version__ = "0.1a1"

if SETTINGS['PaperworkMultiThreading'] == '1':
    models.use_threading = True
    LOGGER.info('Multi threading active')


class PaperworkVim:
    """Interface between vim and view-class.

    Provides functions for autocommands and keybindings.
    """
    def __init__(self):
        """Initializes the interface class."""
        # Not using the global SETTINGS here, since
        # PaperworkHost has no default value.
        self.pw = models.Paperwork(eval('g:PaperworkHost'))
        self.pw.download()
        self.pwbuffers = PaperworkBuffers(self.pw, __version__)
        self.tabs = {}
        self.currTabId = 0
        LOGGER.info('Initialized PaperworkVim')

    def open(self):
        """Open a sidebar."""
        LOGGER.info('Opening Sidebar')
        try:
            self.tabs[get_tab_id()].open_sidebar()
        except:
            self.tabs[self.currTabId] = PaperworkTab(self.pwbuffers)
            set_tab_id(self.currTabId)
            self.currTabId += 1

    def sync(self):
        """Sync the local paperwork session with the remote host."""
        LOGGER.info('Start syncing with remote host')
        self.pw.update()
        LOGGER.info('Finished syncing, updating buffers')
        self.pwbuffers.update_buffers()
        self.pwbuffers.print_sidebar()

    def parse_sidebar(self):
        """Parses sidebar to paperwork."""
        LOGGER.info('Parsing sidebar')
        self.pwbuffers.parse_sidebar_buffer()

    def open_note(self):
        """Opens a note."""
        line = vim.current.line
        if line[0] in default_indent:
            LOGGER.info('Searching note "{}"'.format(line))
            note = self.pw.find_note(parse_title(line))
            if note:
                LOGGER.info('Found note {}'.format(note))
                self.tabs[get_tab_id()].open_note(note)
            else:
                LOGGER.error('No note found'.format(line))

    def write_note(self):
        """Autocmd hook to update a note."""
        note = self.pw.find_note(get_note_id())
        if note:
            LOGGER.info('Writing note {}'.format(note))
            self.pwbuffers.write_note_buffer(note)
        else:
            LOGGER.error('Found no note for {}'.format(get_note_id()))

    def close_note(self):
        """Autocmd hook to delete the temporary file."""
        note = self.pw.find_note(get_note_id())
        LOGGER.info('Closing note {}'.format(note))
        self.pwbuffers.delete_note_buffer(note)
