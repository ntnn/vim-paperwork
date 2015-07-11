if exists('g:PaperworkVersion')
    finish
else
    if globpath(&rtp, 'autoload/webapi/http.vim') == ''
        echoerr 'vim-paperwork requires webapi-vim'
        finish
    endif

    let g:paperwork_version = '0.1a'
    let g:paperwork_uri = 'https://github.com/ntnn/vim-paperwork'
endif

if !paperwork#base#variables_valid()
    finish
endif

if g:paperwork_default_keybinds
    nnoremap <silent> <leader>P :call paperwork#sidebar#open()<CR>
endif

call paperwork#base#autocmd('VimLeave', 'paperwork#base#cleanup')
