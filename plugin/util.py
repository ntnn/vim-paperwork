import vim
import re
import os

tab_var = 't:PaperworkTabId'
note_var = 'b:PaperworkNoteId'
tempfileprefix = 'vim-paperwork-{}'

default_width = vim.eval('g:PaperworkDefaultWidth')
default_indent = vim.eval('g:PaperworkDefaultIndent')


def set_scratch():
    """Configures the current window to be a scratch window."""
    # Scratch buffer
    vim.command('setl buftype=nofile')
    # Not selectable
    vim.command('setl bufhidden=hide')
    # ???
    vim.command('setl noswapfile')
    # Fixed width
    vim.command('setl wfw')

    # Folding
    vim.command('setl foldmethod=expr')
    vim.command("setl foldexpr=PaperworkFoldExpr()")
    vim.command('setl foldtext=getline(v:foldstart)')
    vim.command('setl fillchars=fold:\ ')
    vim.command('setl foldlevel=1')
    vim.command('setl nospell')


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
    return int(vim.eval(tab_var))


def set_tab_id(tab_id):
    """Sets the PaperworkTabId of the current tab."""
    vim.command('let {} = {}'.format(tab_var, tab_id))


def get_note_id():
    """Returns the PaperworkNoteId of the current note."""
    return vim.eval(note_var)


def set_note_id(note_id):
    """Sets the PaperworkNoteId of the current note."""
    vim.command('let {} = {}'.format(note_var, note_id))


def get_filepath(filename):
    """Returns the path for the temporary file."""
    return os.path.join(
        os.path.abspath(os.sep),
        'tmp',
        tempfileprefix.format(
            re.sub(' ', '\ ', filename)))