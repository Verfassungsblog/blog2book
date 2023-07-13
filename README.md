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
./wp2latex --with-footnotes --endnotes --first-letter-before "\lettrine[nindent=0pt,findent=2pt,loversize=0.1]{" --first-letter-after "}{}\normalfont" --convert-links-to-citations --project-template "verfassungsblog-templates/verfassungsbooks" --fix-sections --remove-ulines --zip url-here
````

Convert all blog posts from verfassungsblog.de except debates, editorial posts:
````
python wp2latex.py --with-footnotes "verfassungsblog.de" --fix-sections --zip --remove-ulines --project-template "verfassungsblog-templates/verfassungsblatt" --all-posts --after 2023-04-30T00:00:00 --before 2023-06-01T00:00:00 --exclude-categories 604,2602,4655,875,601 --exclude-categories-recursive --single-post-template latex-templates/verfassungsblatt_single_post.tex
````

## TODO
* improve first letter detection