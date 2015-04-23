#MarkIdea - a simple wiki based on mercurial and markdown for knowledge management
## How to use
install web.py first, see <http://webpy.org/>

install hglib and markdown, if mercurial is not installed on your system, install it first
      
	pip install python-hglib
	pip install markdown

initialize the data repository

	cd data
	hg init data
	
start the server

	python index.py

use your browser navigate to http://localhost:8080
then you go!

see config.ini for further settings
