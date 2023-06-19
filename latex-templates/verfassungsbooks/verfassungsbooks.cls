%% Verfassungsbooks Latex Template
%% Author: Keanu Dölle
%% Email: kd@verfassungsblog.de
%% This is released under the Creative Commons CC BY 4.0 license.

\ProvidesClass{verfassungsbooks}[Verfassungsbooks template v1.0]
\LoadClass[twoside,10pt]{book}

\RequirePackage[
papersize={12.5cm,19cm},
left=1.5cm,
right=1.5cm,
top=1.8cm,
bottom=2.5cm,
footskip=1cm,
]{geometry}
\RequirePackage{fontspec}
\RequirePackage{etoolbox}
\RequirePackage[a-1b]{pdfx}
\RequirePackage{setspace}
\RequirePackage{xcolor}
\RequirePackage{hyperref}
\RequirePackage{xurl}
\RequirePackage{xparse}
\RequirePackage{titlesec}
\RequirePackage{array}
\RequirePackage{qrcode}
\RequirePackage{rotating}
\RequirePackage{lettrine}
\RequirePackage{enotez}
\RequirePackage{xparse}
\RequirePackage{csquotes}
\RequirePackage[main=english]{babel}
\RequirePackage{tikz,tikzpagenodes}
\RequirePackage{fancyhdr}
\RequirePackage{scrextend}
\RequirePackage{ragged2e}
\RequirePackage{tocloft}
\RequirePackage[
backend=biber,
style=apa6,
natbib=true,
ibidtracker=true,
]{biblatex}

\let\footnote\endnote%

\definecolor{hyperlinkgray}{gray}{0.35}

\makeatletter
\let\ps@plain\ps@empty
\makeatother

\newcommand{\emptypage}{
\newpage
\thispagestyle{empty}
\mbox{}
\newpage
}

\newfontfamily\antoniofont{Antonio}[
Path = ./AntonioFont/,
Extension = .ttf,
UprightFont = *-Regular,
BoldFont = *-Bold,
Ligatures=TeX
]
\newfontfamily\pagenumfont{Antonio}[
Path = ./AntonioFont/,
Extension = .ttf,
UprightFont = *-Regular,
SizeFeatures={Size=8},
Ligatures=TeX
]
\newfontfamily\headerfont{PT Serif}[
SizeFeatures={Size=6},
ItalicFont={PT Serif Italic},
ItalicFeatures={Scale=0.6},
Ligatures=TeX
]

%Defining chaptitlepage command
%\chaptitlepage[opt. subtitle][opt. shorttitle]{title}{authors}{link}
\NewDocumentCommand{\chaptitlepage}{o o m m m}{
\Ifthispageodd{}{\emptypage} %Always start on right page
\vspace*{4em}

\begin{center}
\noindent
\textit{#4}\\
\vspace*{4em}
{\antoniofont\Large#3}\\
\vspace*{1em}
{\textit{#1}}
\end{center}

\phantomsection
\addtocontents{toc}{\protect\vspace*{2mm}\noindent\textit{\footnotesize#4}\par\vspace*{-4mm}}
\addcontentsline{toc}{chapter}{#3\ifx&#1&\else: #1\fi}

\chapterqrcode{#5}
\thispagestyle{empty}
\fancyhead[CE]{\headerfont\textit{#4}}
\fancyhead[CO]{\headerfont\IfNoValueTF{#2}{\textit{#3}}{\textit{#2}}}
\emptypage
}

%Hyperlink setup:

\hypersetup{colorlinks=true}

\newcommand{\resethypercolour}{\hypersetup{
    linkcolor=hyperlinkgray,
    filecolor=hyperlinkgray,      
    urlcolor=hyperlinkgray}}
\newcommand{\blackhypercolour}{\hypersetup{
    linkcolor=black,
    filecolor=black,
    urlcolor=black}}

\resethypercolour
\urlstyle{same}
\onehalfspacing
\setmainfont{PT Serif}[Scale=MatchUppercase,ItalicFont={PT Serif Italic}, ItalicFeatures={Scale=0.925}]
\pagestyle{fancy}
\setlength{\parskip}{0mm}
\titlespacing*{\section}{0pt}{4.05mm}{4.05mm}
\titlespacing*{\subsection}{0pt}{1\baselineskip}{1\baselineskip}
\titleformat{\section}{\antoniofont\large}{\thesection}{1em}{}
\titleformat{\subsection}{\normalfont\it}{\thesubsection}{1em}{}

\newcommand{\typsetnoteintext}[1]{{\normalfont\footnotesize\textsuperscript{#1}}}
\setenotez{
list-name = {References},
reset = true, 
mark-cs = {\typsetnoteintext},
list-heading = {\noindent{\antoniofont\large#1}\\},
backref = true
}
\DeclareInstance{enotez-list}{plain}{paragraph}
{
notes-sep = .25\baselineskip,
format = \RaggedRight,
}
\renewcommand{\headrulewidth}{0pt}

\newcommand{\chapterqrcode}[1]{
\blackhypercolour
\begin{tikzpicture}[overlay,remember picture,inner sep=0pt, outer sep=0pt]
\node[anchor=south] at (current page text area.south) {
\href{#1}
  {\XeTeXLinkBox{
  \begin{turn}{45}
\qrcode[height=25mm]{#1}
\end{turn}  
  }}
};
\end{tikzpicture}
\resethypercolour
}
\addto\captionsenglish{
  \renewcommand{\contentsname}%
    {\normalfont\Large Contents}%
}
\fancyhead{}
\fancyfoot{}
\fancyfoot[LE]{\pagenumfont\thepage}
\fancyfoot[RO]{\pagenumfont\thepage}
\setlength{\cftbeforetoctitleskip}{0em}
\renewcommand{\cftchapfont}{\antoniofont}
\renewcommand{\cftchappagefont }{\small\normalfont}
\cftsetrmarg{5em}

\newenvironment{italicquote}{\quote\itshape}{\endquote}
\SetBlockEnvironment{italicquote}