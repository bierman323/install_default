" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
Plugin 'VundleVim/Vundle.vim'

" Git pluggins
Plugin 'tpope/vim-fugitive'
Plugin 'vim-airline/vim-airline'

" Colour Scheme
Plugin 'morhetz/gruvbox'

Plugin 'scrooloose/nerdtree'

call vundle#end()

syntax enable
" Colour schemes used
colorscheme gruvbox
set background=dark
set t_Co=256
" colorscheme koehler

" Nerd tree
let NERDTreeIgnore = ['__pycache__', '\.pyc$', '\.o$', '\.so$', '\.a$', '\.swp', '*\.swp', '\.swo', '\.swn', '\.swh', '\.swm', '\.swl', '\.swk', '\.sw*$', '[a-zA-Z]*egg[a-zA-Z]*', '.DS_Store', '\idea', '\.iml']
let NERDTreeShowHidden=1
let g:NERDTreeWinPos="left"
let g:NERDTreeDirArrows=0
let g:NERDTreeNodeDelimiter = "\u00a0"  "Gets rid of ^G at the start of every line
:nmap <c-e> :NERDTreeToggle<CR>

" Tab movement

nnoremap th  :tabfirst<CR>
nnoremap tj  :tabnext<CR>
nnoremap tk  :tabprev<CR>
nnoremap tl  :tablast<CR>

nnoremap tn  :tabnext<Space>
nnoremap tm  :tabm<Space>
nnoremap td  :tabclose<CR>
" Alternatively use
"nnoremap th :tabnext<CR>
"nnoremap tl :tabprev<CR>
"nnoremap tn :tabnew<CR>

" ==== moving around
nmap <silent> <A-Up> :wincmd k<CR>
nmap <silent> <A-Down> :wincmd j<CR>
nmap <silent> <A-Left> :wincmd h<CR>
nmap <silent> <A-Right> :wincmd l<CR>

set tabstop=2
set shiftwidth=2
set softtabstop=2
set expandtab
set smartindent
set incsearch
set smartcase
set nu
set relativenumber
set backspace=2
set ruler
set hlsearch
set wildmenu
syntax on
set showcmd
autocmd FileType python set tabstop=2|set shiftwidth=2|set expandtab|set backspace=2|set softtabstop=2
autocmd BufWritePre * :%s/\s\+$//e

" Visual block will take base64 code and replace it with decoded text
vnoremap <leader>b y:tabe\|pu!=system('base64 -d', @@)<cr>

"Open up the vimrc in a vertical split
nnoremap <leader>ev :vsplit $MYVIMRC<cr>

"Open up a terminal 50 characters wide
nnoremap <leader>t :vert term ++cols=50<cr>

" Search and replace. With an 'rc' it will do a confirmation before changing
" First you have to hit the *
" Similar to doing * :%s//<ctrl><r></>/bliff/g
nnoremap <leader>r :%s///g<Left><Left>
nnoremap <leader>rc :%s///gc<Left><Left><Left>

"Type s* then the replacement term <esc> and then . to repeat for each instance
"Similar to multiple cursors in other editors
"With visual blocks you can do multiple words (awesome)
nnoremap <silent> s* :let @/='\<'.expand('<cword>').'\>'<cr>cgn
xnoremap <silent> s* "sy:let @/=@s<cr>cgn

"Clear search highlights. The only way I will use highlite search (hlsearch)
map <leader><space> :let @/=''<cr>

" Maps suggested by Primeagen
nmap <leader>gh :diffget //3<cr>
nmap <leader>gu :diffget //2<cr>
nmap <leader>gs :G<cr>

" Run the json formating tool
nmap <leader>jf :%!python -m json.tool indent=2<CR>
nmap <leader>jq :%!jq -S .<CR>

set t_md=

filetype indent plugin on
