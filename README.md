# django-blog

This is an old blog app I built when I was trying to learn Django back in 2008. I actually used it as the main blog engine for https://roytang.net for a while, before I decided switching to a standard package like Wordpress might be easier. I currently have no intention of updating it, this repo is for archival purposes only.

Documentation of the development can be found via the "royondjango" tag on my blog: https://roytang.net/tag/royondjango/

The code is fairly old, I couldn't run it anymore using Django 2.12 + Python 3. Was able to run it using Django 1.1.3 and Python 2.7.12. (You might need to create the data/devdb sqlite3 database, since I did not upload my own devdb to github)

The source code includes several third-party Django applications, I don't think we had `pip install` back in 2008, so they just exist directly in the project folder. More information on those third-party apps can be found in the colophon: https://roytang.net/2008/12/colophon-2008/

There's a lot of hardcoded stuff particularly in the templates that still reference my site url (https://roytang.net).