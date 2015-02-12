import vim
import tempfile
import string
import logging

LOGGER = logging.getLogger(__name__)

TAB_VAR = 't:PaperworkTabId'
NOTE_VAR = 'b:PaperworkNoteId'

TEMPFILEPREFIX = 'vim-paperwork-'
VALID_CHARS = "-_.() {}{}".format(string.ascii_letters, string.digits)

SETTINGS = {
    'PaperworkDefaultWidth': 50,
    'PaperworkDefaultIndent': vim.eval(
        "&expandtab ? repeat(' ', &shiftwidth) : '\t'"),
    'PaperworkDefaultNotebook': None,
    'PaperworkDefaultNoteWindow': 'split',
    'PaperworkSidebarFolding': 1,
    'PaperworkSidebarHighlight': 1,
    'PaperworkSidebarTimeout': 50,
    'PaperworkDebug': 0,
    'PaperworkMultiThreading': 0
    }


def parse_settings():
    def get(var, value):
        return cmd("get(g:, '{}', {})").format(var, value)
    for setting in SETTINGS:
        SETTINGS[setting] = get(SETTINGS[setting])


def coll_to_list(coll):
    """Turns the collection into a list.

    :type coll: list of Note or Tag
    :rtype: list
    """
    ret = []
    note_s = 'Notes' if len(coll.notes) != 1 else 'Note'
    ret.append('{} - {} {}'.format(coll.title, len(coll.notes), note_s))
    for note in coll.get_notes():
        ret.append(SETTINGS['PaperworkDefaultIndent'] + note.title)
    ret.append('')
    return ret


def get_tempfile(suffix=''):
    """Returns a temporary file.

    :type suffix: str
    :rtype: NamedTemporaryFile
    """
    LOGGER.info('Creating tempfile')
    if suffix != '':
        suffix = ''.join(char for char in suffix if char in VALID_CHARS)
        suffix = '-' + suffix.replace(' ', '_')
    return tempfile.NamedTemporaryFile(
        prefix=TEMPFILEPREFIX,
        suffix=suffix)


def parse_title(title):
    """Returns the title of a sidebar entry.

    :type title: str
    :rtype: str
    """
    LOGGER.info('Parsing title {}'.format(title))
    if title[0] in (' ', '\t'):
        return title[len(SETTINGS['PaperworkDefaultIndent']):]
    elif '-' in title:
        return title[:title.rindex(' -')]
    else:
        return title


def set_folding():
    """Configures the current window to be a scratch window.

    :type highlight: bool
    """
    LOGGER.info('Setting sidebar options')
    cmd('setl bufhidden=hide')
    cmd('setl wfw')
    cmd('setl timeoutlen={}'.format(SETTINGS['PaperworkSidebarTimeout']))
    cmd('setl nospell')
    if SETTINGS['PaperworkSidebarFolding']:
        LOGGER.info('Using sidebar expression')
        cmd('setl foldmethod=expr')
        cmd('setl foldexpr=PaperworkFoldExpr()')
        cmd('setl foldtext=getline(v:foldstart)')
        cmd('setl fillchars=fold:\ ')
        cmd('setl foldlevel=1')
    if SETTINGS['PaperworkSidebarHighlight']:
        LOGGER.info('Using sidebar highlight')
        cmd('hi Folded term=NONE cterm=NONE gui=NONE')


def cmd(command):
    """Command to execute in vim.

    :type command: string
    """
    LOGGER.info('Executing command {}'.format(command))
    vim.command(command)


def eval(expr):
    """Evaluates expression in vim.

    :type expr: str
    :rtype: str
    """
    LOGGER.info('Getting var {}'.format(expr))
    return vim.eval(expr)


def set_var(var, value):
    """Sets variable in vim.

    :type var: str
    :type value: str or int
    """
    cmd('let {} = {}'.format(var, value))


def get_tab_id():
    """Returns the PaperworkTabId of the current tab.

    :rtype: int
    """
    return int(eval(TAB_VAR))


def set_tab_id(tab_id):
    """Sets the PaperworkTabId of the current tab.

    :type tab_id: int or str
    """
    set_var(TAB_VAR, tab_id)


def get_note_id():
    """Returns the PaperworkNoteId of the current note.

    :rtype: int
    """
    return int(eval(NOTE_VAR))


def set_note_id(note_id):
    """Sets the PaperworkNoteId of the current note.

    :type note_id: int
    """
    cmd('let {} = {}'.format(NOTE_VAR, note_id))



















