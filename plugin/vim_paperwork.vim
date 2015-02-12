if !has('python')
    echo 'Error: vim-paperwork requires python'
    finish
endif

if !exists('g:PaperworkHost')
    echo 'Error: vim-paperwork requires g:PaperworkHost to be set.'
    finish
endif

py sys.path.append(vim.eval('expand("<sfile>:h")'))
py from vim_paperwork.vim_paperwork import PaperworkVim
py pv = None

function! PaperworkOpenSidebar()
python << endPython
if not pv:
    pv = PaperworkVim()
if not pv.pw.authenticated:
    print('User/password combination is not valid or host can not be reached.')
else:
    pv.open()
endPython
endfunction

function! PaperworkOpenNote()
python << endPython
pv.open_note()
endPython
endfunction

function! PaperworkSync()
python << endPython
pv.sync()
endPython
endfunction

function! PaperworkNoteBufferWrite()
python << endPython
pv.write_note()
endPython
endfunction

function! PaperworkNoteBufferDelete()
python << endPython
pv.close_note()
endPython
endfunction

fu! PaperworkSidebarChanged()
python << endPython
pv.parse_sidebar()
endPython
endfu

function! PaperworkFoldExpr()
    let prevline = getline(v:lnum - 1)
    let line = getline(v:lnum)

    " exclude headers
    if line =~ '^+'
        return -1
    endif

    " notebooks/tags
    if line =~ '^\w'
        return '1>'
    endif

    " blanks
    if line =~ '^$'
        if prevline =~ '^+'
            return -1
        endif
        return '<1'
    endif
    return '1'
endfunction
