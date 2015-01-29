if !has('python')
    echo 'Error: vim-paperwork requires python'
    finish
endif

if !exists('g:PaperworkHost') || !exists('g:PaperworkUser') || !exists('g:PaperworkPassword')
    echo 'Error: vim-paperwork requires host, user and password.'
    finish
endif

if !exists('g:PaperworkDefaultWidth')
    let g:PaperworkDefaultWidth = 50
endif

if !exists('g:PaperworkDefaultIndent')
    let g:PaperworkDefaultIndent = &expandtab ? repeat(' ', &shiftwidth) : '\t'
endif

if !exists('g:PaperworkDefaultNotebook')
    let g:PaperworkDefaultNotebook = 'All Notes'
endif

if !exists('g:PaperworkUsePwFolding')
    let g:PaperworkUsePwFolding = 1
endif

if !exists('g:PaperworkUsePwHighlight')
    let g:PaperworkUsePwHighlight = 1
endif

py sys.path.append(vim.eval('expand("<sfile>:h")'))
py from vim_paperwork import PaperworkVim
py pv = None

function! PaperworkOpenSidebar()
python << endPython
if not pv:
    pv = PaperworkVim()
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
