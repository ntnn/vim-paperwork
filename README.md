# vim-paperwork
[paperwork](https://github.com/twostairs/paperwork) is 'an open source note-taking and archiving tool'.  

vim-paperwork allows you to create, edit and delete notes from vim.  Vim folds
are used to display notebooks, thus default and personal keybindings can be
used to navigate the sidebar.

The final aim of this plugin is to provide a seamless interface to the users
notes, while not needing any keybindings aside from the one opening the
sidebar.

# Install
Install this plugin with your preferred plugin-manager.  
`vim-paperwork` requires [webapi-vim](https://github.com/mattn/webapi-vim)

Define the following variables:  
```viml
g:paperwork_host = 'host'
g:paperwork_user = 'user'
g:paperwork_password = 'password'
```

# Usage
Currently only editing of existing notes is possible.

## Sidebar
Per default the sidebar can be opened with `<leader>P`, pressing enter on a
note entry closes the sidebar and opens the note in a new buffer.

## Editing notes
`:write` and equivalents writes the note to the temporary file and updates the
note on the remote host.  
`:quit` and equivalents deletes the buffer and the temporary file.


#I found a bug/issue!
If you got the message 'Error! HTTP status code: [...]' please submit an issue
with the output that was appended to the current buffer.

If you encountered another problem, execute `let g:paperwork_debug = 1`, try
to replicate it, then execute `call paperwork#base#messages_save()` in an empty
buffer and add the output to your issue.
