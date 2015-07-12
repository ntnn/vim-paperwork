fu! paperwork#buffer#replace(text)
    if type(a:text) == type([])
        let l:text = join(a:text, "\n")
    else
        let l:text = a:text
    endif

    " save paste setting and reapply it afterwards
    let l:paste = &paste
    set paste

    " Mark current position
    normal! m'
    normal! 1,$d
    execute 'normal! 1S' . l:text
    " silent for sidebar buffer
    silent! normal! w!
    normal! ''

    let &paste = l:paste
endfu

fu! paperwork#buffer#append(text)
    call append(line('$'), a:text)
endfu
