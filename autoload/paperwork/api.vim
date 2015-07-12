let s:api_root = '/api/v1/'
let s:header = {
            \ 'Authorization': 'Basic ' . webapi#base64#b64encode(g:paperwork_user . ':' . g:paperwork_password),
            \ 'Content-Type': 'application/json'
            \ }

fu! s:request(func, node, ...)
    let l:url = g:paperwork_host . s:api_root . a:node
    call paperwork#base#debug('URL:' . l:url)

    " a:1 (the json dict) is being passed inside a list (probably because of
    " call) so we have to unpack the list _if_ it is a list
    let l:param = (a:0 > 0 && len(a:1) >= 1)? webapi#json#encode(a:1[0]) : ''
    call paperwork#base#debug('Parameter: ' . string(l:param))

    let l:callback = (a:0 > 0 && len(a:1) >= 2 )? a:1[1] : 0
    call paperwork#base#debug('Callback: ' . l:callback)

    " Grabs the method (a:2) if passed, since put/delete can only be passed
    " over post
    let l:method = (a:0 > 1)? a:2 : ''
    call paperwork#base#debug('Method: ' . a:func . ' ' . l:method)

    if l:callback && g:paperwork_async
        call paperwork#base#debug('Using async')
        call xolox#misc#async#call({
                    \ 'function': 'webapi#http#' . a:func,
                    \ 'arguments': [l:url, l:param, s:header, l:method],
                    \ 'callback': l:callback,
                    \ })
        return
    endif

    let l:ret = call('webapi#http#' . a:func, [l:url, l:param, s:header, l:method])
    if l:ret['status'] != '200'
        " An error during the
        echoerr 'Error! HTTP status code: ' . l:ret['status']
        echoerr 'The full reponse is being appended to your current buffer, if the problem persists while your paperwork server works fine please submit an issue at ' . g:paperwork_uri
        call append(line('$'), string(l:ret))
        return
    endif

    return webapi#json#decode(l:ret['content'])['response']
endfu

fu! s:get(node, ...)
    return call('s:request', ['get', a:node, a:000])
endfu

fu! s:post(node, ...)
    return call('s:request', ['post', a:node, a:000])
endfu

fu! s:put(node, ...)
    " PUT and DELETE need to be passed as the second variable argument, since
    " webapi#http#post only provides post/get, whiel others have to be done via
    " post
    return call('s:request', ['post', a:node, a:000, 'PUT'])
endfu

fu! s:delete(node, ...)
    return call('s:request', ['post', a:node, a:000, 'DELETE'])
endfu

fu! paperwork#api#notebooks_list()
    return s:get('notebooks')
endfu

fu! paperwork#api#notebook_create(title)
    return s:post('notebooks', {
                \ 'title': a:title,
                \ 'type': '0',
                \ })
endfu

fu! paperwork#api#notebook_get(notebook_id)
    return s:get('notebooks/' . a:notebook_id)
endfu

fu! paperwork#api#notebook_update(notebook_id, title)
    return s:put('notebooks/' . a:notebook_id, {
                \ 'title': a:title,
                \ 'type': '0'
                \ }, '')
endfu

fu! paperwork#api#notebook_delete(notebook_id)
    return s:delete('notebooks/' . a:notebook_id, '')
endfu

fu! paperwork#api#notes_list(notebook_id)
    return s:get('notebooks/' . a:notebook_id . '/notes')
endfu

fu! paperwork#api#note_create(notebook_id, title, content)
    return s:post('notebooks/' . a:notebook_id . '/notes', {
                \ 'title': a:title,
                \ 'content': a:content,
                \ })
endfu

fu! paperwork#api#note_get(notebook_id, note_id)
    return s:get('notebooks/' . a:notebook_id . '/notes/' . a:note_id)
endfu

fu! paperwork#api#note_update(notebook_id, note_id, title, content)
    return s:put('notebooks/' . a:notebook_id . '/notes/' . a:note_id, {
                \ 'title' : a:title,
                \ 'content': a:content,
                \ }, '')
endfu

fu! paperwork#api#note_delete(notebook_id, note_id)
    return s:delete('notebooks/' . a:notebook_id . '/notes/' . a:note_id, {}, '')
endfu

fu! paperwork#api#note_move(notebook_id, note_id, newnotebook_id)
    return s:get('notebooks/' . a:notebook_id . '/notes/' . a:note_id . '/move/' . a:newnotebook_id, {}, '')
endfu

fu! paperwork#api#note_versions(notebook_id, note_id)
    return s:get('notebooks/' . a:notebook_id . '/notes/' . a:note_id, '/versions')
endfu

fu! paperwork#api#note_version_get(notebook_id, note_id, version_id)
    return s:get('notebooks/' . a:notebook_id . '/notes/' . a:note_id, '/versions/' . a:version_id)
endfu
