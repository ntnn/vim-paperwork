from paperworks import models

from view import *  # noqa
from util import *  # noqa

import vim
import logging

if vim.eval('g:PaperworkDebug') == '1':
    handler = logging.FileHandler(
        'vim-paperwork.log', mode='w')
    handler.formatter = logging.Formatter(
        '%(asctime)s [%(levelname)-5s @ '
        '%(filename)-10s:%(funcName)-15s:%(lineno)-4s] '
        '%(process)-6s - %(message)s')
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)

version = "0.1a1"

host = vim.eval('g:PaperworkHost')

default_indent = vim.eval('g:PaperworkDefaultIndent')

if vim.eval('g:PaperworkMultiThreading') == '1':
    models.use_threading = True
    logger.info('Multithreading active')


class PaperworkVim:
    def __init__(self):
        self.pw = models.Paperwork(host)
        self.pw.download()
        self.pwbuffers = PaperworkBuffers(self.pw, version)
        self.tabs = {}
        self.currTabId = 0
        logger.info('Initialized PaperworkVim')

    def open(self):
        """Open a sidebar."""
        logger.info('Opening Sidebar')
        try:
            self.tabs[util.get_tab_id()].open_sidebar()
        except:
            self.tabs[self.currTabId] = PaperworkTab(self.pwbuffers)
            util.set_tab_id(self.currTabId)
            self.currTabId += 1

    def sync(self):
        """Sync the local paperwork session with the remote host."""
        logger.info('Start syncing with remote host')
        self.pw.update()
        logger.info('Finished syncing, updating buffers')
        self.pwbuffers.update_buffers()
        self.pwbuffers.print_sidebar()

    def parse_sidebar(self):
        logger.info('Parsing sidebar')
        self.pwbuffers.parse_sidebar_buffer()

    def open_note(self):
        """Opens a note."""
        line = vim.current.line
        if line[0] in default_indent:
            logger.info('Searching note "{}"'.format(line))
            note = self.pw.find_note(util.parse_title(line))
            if note:
                logger.info('Found note {}'.format(note))
                self.tabs[util.get_tab_id()].open_note(note)
            else:
                logger.error('No note found'.format(line))

    def write_note(self):
        """Autocmd hook to update a note."""
        note = self.pw.find_note(util.get_note_id())
        if note:
            # logger.info('Writing note {}'.format(note))
            logger.info('Writing note {}'.format(note))
            self.pwbuffers.write_note_buffer(note)
        else:
            logger.error('Found no note for {}'.format(util.get_note_id()))

    def close_note(self):
        """Autocmd hook to delete the temporary file."""
        note = self.pw.find_note(util.get_note_id())
        logger.info('Closing note {}'.format(note))
        self.pwbuffers.delete_note_buffer(note)
