#vim-paperwork

[paperwork](https://github.com/twostairs/paperwork) is 'an open source note-taking and archiving tool'.  

vim-paperwork allows you to create, edit and delete notes from vim.  
Vim folds are used to display notebooks, thus default and personal keybindings can be used to navigate the sidebar.

The final aim of this plugin is to provide a seamless interface to the users notes, while not needing many keybindings aside from
the one opening the sidebar.

#Usage
To add notebooks and notes the desired title can be inserted.
Titles can be directly edited.
vim-paperwork automatically parses changes and pushes them to the remote host.

Writing (`:write` and equivalents) in the sidebar-buffer forces an update to the remote host -
means that local values will overwrite the remote values.  
Editing (`:edit` and equivalents) in the sidebar-buffer syncs the local and remote files, taking the most recent version each.

Writing a note forces an update to the remote host, while edit only rereads the temporary file.  
To force an update of a note you need to sync through the sidebar buffer (or via shortcut).

Bind 'PaperworkOpenSidebar()' to open the sidebar:  
`nnoremap <silent> <leader>P :call PaperworkOpenSidebar()<CR>`

vim-paperwork downloads information from remote after the first call, so e.g. deactivating until call with vim-plug is not necessary.
But this also means that the first start can take a few seconds, depending on the amount of notes and your connection.

#Screenshot

With paperwork default settings:  
![example-screenshot](https://raw.githubusercontent.com/ntnn/vim-paperwork/master/screenshots/sidebar_note.png)
