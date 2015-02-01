#vim-paperwork
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/ntnn/vim-paperwork/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/ntnn/vim-paperwork/?branch=master)  
[paperwork](https://github.com/twostairs/paperwork) is 'an open source note-taking and archiving tool'.  

vim-paperwork allows you to create, edit and delete notes from vim.  
Vim folds are used to display notebooks, thus default and personal keybindings can be used to navigate the sidebar.

The final aim of this plugin is to provide a seamless interface to the users notes, while not needing any keybindings aside from
the one opening the sidebar.

#Install
Install this plugin with your preferred plugin-manager.  
`paperwork.py` is required, install it either through `pip install paperworks` or
clone the [github repo](https://github.com/ntnn/paperwork.py) and install it with setuptools.  

Define the following variables:  
```viml
let g:PaperworkHost = host
let g:PaperworkUser = user
let g:PaperworkPassword = password
```

#Usage
To add notebooks and notes the desired title can be inserted.
Titles can be directly edited.
vim-paperwork automatically parses changes and pushes them to the remote host.

Writing (`:write` and equivalents) in the sidebar-buffer forces an update to the remote host -
means that local values will overwrite the remote values.  
Editing (`:edit` and equivalents) in the sidebar-buffer syncs the local and remote files, taking the most recent version each.

Writing a note forces an update to the remote host, while edit only rereads the temporary file.  
To force an update of a note you need to sync through the sidebar buffer (or via shortcut).

Bind `PaperworkOpenSidebar()` to open the sidebar:  
`nnoremap <silent> <leader>P :call PaperworkOpenSidebar()<CR>`

vim-paperwork downloads information from remote after the first call, so e.g. deactivating until call with vim-plug is not necessary.
But this also means that the first start can take a few seconds, depending on the amount of notes and your connection.

#Screenshot

With paperwork default settings, link to asciinema.org recording:  
[![example-screenshot](https://raw.githubusercontent.com/ntnn/vim-paperwork/master/screenshots/example_screenshot.png)](https://asciinema.org/a/15958)


#I found a bug/issue!
If you encountered a problem, please put this into your vimrc and try to replicate it:  
`let g:PaperworkDebug = 1`  
This creates a log file in the directory in which you are starting Vim. Try to replicate the problem and file an issue here on github with the content of the log file.
Just don't forget to disable the line afterwards, otherwise you'll have dozens of log files all over your system.
