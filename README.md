# wp2latex
Convert your wordpress blog articles to books, journals, etc. via LaTeX and this tool.

## Installation
Download the latest release and unzip the latex-templates folder.

## Example Usage
Convert post to LaTeX post:
``./wp2latex "https://verfassungsblog.de/ist-der-umgang-mit-klimaprotesten-in-deutschland-menschenrechtswidrig/"``

Convert single post to latex post, extracting footnotes, converting footnotes to endnotes and first big letter via lettrine package and convert links to citations:

````
./wp2latex 
--with-footnotes
--endnotes
--first-letter-before "\lettrine[nindent=0pt,findent=2pt,loversize=0.1]{"
--first-letter-after "}{}\normalfont"
--convert-links-to-citations
"https://verfassungsblog.de/ist-der-umgang-mit-klimaprotesten-in-deutschland-menschenrechtswidrig/"
````

Convert category with several posts to a book:
````
./wp2latex --with-footnotes --endnotes --first-letter-before "\lettrine[nindent=0pt,findent=2pt,loversize=0.1]{" --first-letter-after "}{}\normalfont" --convert-links-to-citations --project-template "latex-templates/verfassungsbooks" --fix-sections --remove-ulines "https://verfassungsblog.de/category/debates/kleben-und-haften-ziviler-ungehorsam-in-der-klimakrise/"
````

## TODO-Liste
* Links die nicht automatisch zitiert werden konnten irgendwie kenntlich machen
* improve first letter detection
* automatically create zip file of output directory