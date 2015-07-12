fu! s:default_set(var, value)
    " Sets variable a:var if it hasn't been set by the user
    if !exists(a:var)
        execute 'let ' . a:var . '=' . a:value
        call paperwork#base#debug(a:var . ' loaded with default ' . a:value)
    endif
endfu

fu! paperwork#base#debug(message)
    " Prints a debug message
    if g:paperwork_debug == 1
        echomsg 'DEBUG:vim-paperwork:' . a:message
    endif
endfu

fu! paperwork#base#messages_save()
    redir => l:messages
    :messages
    redir END
    call paperwork#buffer#replace(l:messages)
endfu

fu! paperwork#base#variables_valid()
    " Checks mandatory and optional variables
    let l:valid = 1
    let l:prefix = 'g:paperwork_'

    let l:variables = ['host', 'user', 'password']
    for l:var in l:variables
        let l:var = l:prefix . l:var
        if !exists(l:var)
            echoerr l:var . ' needed'
            let l:valid = 0
        endif
    endfor

    if !l:valid
        return l:valid
    endif

    let l:defaults = {
                \ 'debug': 0,
                \ 'sidebar_width': 40,
                \ 'sidebar_indent': eval("&expandtab ? '\"' . repeat(' ', &shiftwidth) . '\"' : '\t'"),
                \ 'sidebar_folding': 1,
                \ 'sidebar_highlight': 1,
                \ 'sidebar_timeout': 0,
                \ 'default_keybinds': 1,
                \ 'tempfile_path': "'/tmp/'",
                \ 'tempfile_prefix': "'vim-paperwork-'",
                \ }

    for l:key in keys(l:defaults)
        call s:default_set(l:prefix . l:key, l:defaults[l:key])
    endfor

    return l:valid
endfu

fu! paperwork#base#pull()
    " Pulls notebooks and notes from the server and parses them into
    " a dictionary
    let g:paperwork_notebooks = {}

    for l:notebook in paperwork#api#notebooks_list()
        " Ignore 'All Notes' dictionary
        if l:notebook['type'] != 2
            call paperwork#base#debug('Parsing notebook ' . l:notebook['title'] . ' with id '. l:notebook['id'])
            let l:notebook = {
                        \ 'id': l:notebook['id'],
                        \ 'title': l:notebook['title'],
                        \ 'notes': {},
                        \ }

            for l:note in paperwork#api#notes_list(l:notebook['id'])
                let l:note = {
                            \ 'id': l:note['id'],
                            \ 'notebook_id': l:note['notebook_id'],
                            \ 'title': l:note['version']['title'],
                            \ 'content': l:note['version']['content'],
                            \ }
                call paperwork#base#debug('Parsed note ' . l:note['title'] . ' with id ' . l:note['id'])
                let l:notebook['notes'][l:note['id']] = l:note
            endfor

            let g:paperwork_notebooks[l:notebook['id']] = l:notebook
            call paperwork#base#debug('Finished parsing notebook ' . l:notebook['id'])
        else
            call paperwork#base#debug('Ignoring all notes notebook')
        endif
    endfor
endfu

fu! paperwork#base#nnoremap(key, func)
    execute 'nnoremap <silent> <buffer> ' . a:key . ' :call ' . a:func . '()<CR>'
endfu

fu! s:autocmd_create(groups, func)
    call paperwork#base#debug('Creating augroup ' . a:func . ' for group ' . a:groups)
    " Use augroups to prevent creating a lot of the same autocmds with an
    " augroup named after the function to be called
    execute 'augroup ' . a:func
        " Delete all existing commands in this group
        au!
        execute 'au ' . a:groups . ' call ' . a:func . '()'
    aug END
endfu

fu! paperwork#base#autocmd_buffer(groups, func)
    call s:autocmd_create(a:groups . ' <buffer>', a:func)
endfu

fu! paperwork#base#autocmd(groups, func)
    call s:autocmd_create(a:groups . ' *', a:func)
endfu

fu! paperwork#base#cleanup()
    " Deletes all temporary files
    call delete(expand(g:paperwork_tempfile_path . g:paperwork_tempfile_prefix . '*'))
endfu

