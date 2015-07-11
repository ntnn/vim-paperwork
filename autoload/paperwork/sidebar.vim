let s:spacer = repeat(g:paperwork_sidebar_indent, 8)

fu! paperwork#sidebar#open()
    call paperwork#base#debug('Opening sidebar')

    execute 'vertical topleft ' . g:paperwork_sidebar_width . ' new'
    setl ft=paperwork
    call paperwork#base#debug('Writing info to sidebar')
    call paperwork#buffer#replace(['+++ vim-paperwork ' . g:paperwork_version . ' +++', '', '+++ Notebooks +++'])

    " Pulls notebooks and notes from the server
    call paperwork#base#pull()

    call paperwork#base#debug('Writing notebooks and notes to sidebar')
    for l:notebook_id in keys(g:paperwork_notebooks)
        let l:notebook = g:paperwork_notebooks[l:notebook_id]

        call paperwork#buffer#append(l:notebook['title'] . s:spacer . l:notebook['id'])
        for l:note_id in keys(l:notebook['notes'])
            let l:note = l:notebook['notes'][l:note_id]
            call paperwork#buffer#append(g:paperwork_sidebar_indent . l:note['title'] . s:spacer . l:note['id'] . s:spacer . l:notebook_id)
        endfor

        call paperwork#buffer#append('')
    endfor
    call paperwork#base#debug('Finished sidebar')
endfu

fu! paperwork#sidebar#delete()
    call paperwork#base#debug('Leaving sidebar')
    execute 'set timeoutlen =' . b:timeoutlen
    bdelete!
endfu
