let &t_Co=256 "pour que les colorscheme non-default fonctionnent
if has('gui_running')
	color Base2Tone_MorningLight
else
	color desert
endif



set number
set list
set autoindent
set hlsearch
set cursorline
set foldmethod=indent
set foldnestmax=1
set ignorecase
set smartcase
set mouse=a
set linebreak "wrap line on non-word chars
set autochdir "auto locate to current file
set clipboard=unnamedplus
set listchars=tab:\|\ 
set iskeyword+=/ "char / is not a word separator
map <C-z> <Nop> "disable fucking ctrl+z
cmap x<CR> w<CR>
nnoremap <F2> :set spell<CR><BAR>:set spelllang=en<CR>
nnoremap <F3> :set spell<CR><BAR>:set spelllang=fr<CR>


"éviter échappement pour regex
nnoremap / /\v
vnoremap / /\v
cnoremap %s/ %smagic/
cnoremap \>s/ \>smagic/
"nnoremap :g/ :g/\v
"nnoremap :g// :g//



" Search for selected text, forwards or backwards.
vnoremap <silent> * :<C-U>
  \let old_reg=getreg('"')<Bar>let old_regtype=getregtype('"')<CR>
  \gvy/<C-R><C-R>=substitute(
  \escape(@", '/\.*$^~['), '\_s\+', '\\_s\\+', 'g')<CR><CR>
  \gV:call setreg('"', old_reg, old_regtype)<CR>
vnoremap <silent> # :<C-U>
  \let old_reg=getreg('"')<Bar>let old_regtype=getregtype('"')<CR>
  \gvy?<C-R><C-R>=substitute(
  \escape(@", '?\.*$^~['), '\_s\+', '\\_s\\+', 'g')<CR><CR>
  \gV:call setreg('"', old_reg, old_regtype)<CR>

let @f = "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\\begin{frame}\n\\frametitle{}\n\n\n\\end{frame}\n"
let @o = "\twith open(sys.argv[1],mode=\"r\",encoding=\"utf-8\") as f:\n"
let @i="\\begin{itemize}\n\t\\item\n\\end{itemize}"
let @s="sys.stderr.write(\"\\n\")"
let @d="for key in sorted(d, key=d.get, reverse=True):"
let @p="soup.find_all('div', {'class': 'value'})"


autocmd BufNewFile *.py 0put =\"#!/usr/bin/python\<nl># -*- coding:utf-8 -*-\<nl>\"|$

"don't overwrite register when pasting
" I haven't found how to hide this function (yet)
function! RestoreRegister()
  let @" = s:restore_reg
  return ''
endfunction

function! s:Repl()
    let s:restore_reg = @"
    return "p@=RestoreRegister()\<cr>"
endfunction

" NB: this supports "rp that replaces the selection by the contents of @r
vnoremap <silent> <expr> p <sid>Repl()
