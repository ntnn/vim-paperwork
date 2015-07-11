fu! s:filename_get(id)
    " TODO (Nelo Wallus): Sanitize name and use it together with id for easier
    " locating in bufferlist, CtrlP, Unite, ...
    return g:paperwork_tempfile_path . g:paperwork_tempfile_prefix . a:id
endfu

fu! paperwork#note#open()
    " splitting the line by indent will cause empty entries, of which all
    " succeeding copies will be removed with uniq() the remaining two in
    " between are caught in l:empty and expire with the scope
    let l:line = uniq(split(getline('.'), g:paperwork_sidebar_indent))

    " If the list does not contain 5 entries the current line isn't an already
    " registered note and can't be opened
    " TODO (Nelo Wallus): Create note on demand
    if len(l:line) != 5
        echomsg 'Not a registered note'
        return
    endif

    " Close sidebar
    call paperwork#sidebar#delete()
    call paperwork#base#debug('Closed sidebar, opening temp file')

    " TODO (Nelo Wallus): Use bufnr to identify if note is already opened
    execute 'edit! ' . s:filename_get(l:line[2])

    let [b:title, l:empty, b:id, l:empty, b:notebook_id] = l:line
    call paperwork#buffer#replace(split(g:paperwork_notebooks[b:notebook_id]['notes'][b:id]['content'], '\n'))

    call paperwork#base#autocmd_buffer('BufWritePost', 'paperwork#note#write')
endfu

fu! paperwork#note#write()
    let l:content = join(getline(1, '$'))
    call paperwork#base#debug('Updating note on remote host')
    call paperwork#api#note_update(b:notebook_id, b:id, b:title, l:content)

    call paperwork#base#debug('Host updated, updating local dict')
    let g:paperwork_notebooks[b:notebook_id]['notes'][b:id]['content'] = l:content
endfu
