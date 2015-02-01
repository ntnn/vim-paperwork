import vim
import tempfile
import string
import logging
logger = logging.getLogger(__name__)

tab_var = 't:PaperworkTabId'
note_var = 'b:PaperworkNoteId'
tempfileprefix = 'vim-paperwork-'
valid_chars = "-_.() {}{}".format(string.ascii_letters, string.digits)

default_width = vim.eval('g:PaperworkDefaultWidth')
default_indent = vim.eval('g:PaperworkDefaultIndent')


def set_folding(highlight):
    """Configures the current window to be a scratch window."""
    logger.info('Setting sidebar folding')
    vim.command('setl foldmethod=expr')
    vim.command('setl foldexpr=PaperworkFoldExpr()')
    vim.command('setl foldtext=getline(v:foldstart)')
    vim.command('setl fillchars=fold:\ ')
    vim.command('setl foldlevel=1')
    vim.command('setl nospell')
    if highlight:
        vim.command('hi Folded term=NONE cterm=NONE gui=NONE')


def coll_to_list(coll):
    """Turns the collection into a list."""
    ret = []
    note_s = 'Notes' if len(coll.notes) != 1 else 'Note'
    ret.append('{} - {} {}'.format(coll.title, len(coll.notes), note_s))
    for note in coll.get_notes():
        ret.append(default_indent + note.title)
    ret.append('')
    return ret


def get_tab_id():
    """Returns the PaperworkTabId of the current tab."""
    logger.info('Getting tab id')
    return int(vim.eval(tab_var))


def set_tab_id(tab_id):
    """Sets the PaperworkTabId of the current tab."""
    logger.info('Setting tab id')
    vim.command('let {} = {}'.format(tab_var, tab_id))


def get_note_id():
    """Returns the PaperworkNoteId of the current note."""
    note_id = vim.eval(note_var)
    logger.info('Getting note id {}'.format(note_id))
    return int(note_id)


def set_note_id(note_id):
    """Sets the PaperworkNoteId of the current note."""
    logger.info('Setting note id {}'.format(note_id))
    vim.command('let {} = {}'.format(note_var, note_id))


def get_tempfile(suffix=''):
    """Returns a temporary file."""
    logger.info('Creating tempfile')
    if suffix != '':
        suffix = ''.join(char for char in suffix if char in valid_chars)
        suffix = '-' + suffix.replace(' ', '_')
    return tempfile.NamedTemporaryFile(
        prefix=tempfileprefix,
        suffix=suffix)


def parse_title(title):
    """Returns the title of a sidebar entry."""
    logger.info('Parsing title {}'.format(title))
    if title[0] in (' ', '\t'):
        return title[len(default_indent):]
    elif '-' in title:
        return title[:title.rindex(' -')]
    else:
        return title
