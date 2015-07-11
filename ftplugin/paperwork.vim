fu! PaperworkFoldExpr()
    let prevline = getline(v:lnum - 1)
    let line = getline(v:lnum)

    " exclude headers
    if line =~ '\m^+'
        return -1
    endif

    " notebooks
    if line =~ '\m^[\w\s]\+$' . g:paperwork_sidebar_indent
        return '1>'
    endif

    " blanks
    if line =~ '\m^$'
        if prevline =~ '\m^+'
            return -1
        endif
        return '<1'
    endif
    return '1'
endfu

setl bufhidden=hide
" Keeps the window width when other windows are opened or closed
setl winfixwidth
" Keeping timeoutlen to reset in paperwork#sidebar#delete since it can't be
" set local
let b:timeoutlen = &timeoutlen
execute 'set timeoutlen=' . g:paperwork_sidebar_timeout
setl nospell
" Disable wrapping, since the identifiers for notes and notebooks are kept out
" of sight with spacers
setl nowrap

if g:paperwork_sidebar_folding
    setl foldmethod=expr
    setl foldexpr=PaperworkFoldExpr()
    setl foldtext=getline(v:foldstart)
    setl fillchars="fold:\ "
    setl foldlevel=1
endif

if g:paperwork_sidebar_highlight
    hi Folded term=NONE cterm=NONE gui=NONE
endif

call paperwork#base#nnoremap('<CR>', 'paperwork#note#open')
call paperwork#base#autocmd_buffer('BufLeave', 'paperwork#sidebar#delete')
