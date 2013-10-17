django ERP
==========

**Django ERP** is an _open-source_, _user-oriented_, *ERP system* based on [Django](http://www.djangoproject.com) framework.

Pre-requisites
--------------

Make sure you have the following pre-requisites installed:

 * **python** >= 2.7 (required)
   http://www.python.org

 * **pytz** >= 2011h (required)
   http://pytz.sourceforge.net/

 * **django** >= 1.5.4 (required)
   http://www.djangoproject.com

 * **south** >= 0.7.3 (optional)
   http://south.aeracode.org/

 * **apache2** (optional)
   http://httpd.apache.org

 * **mod_wsgi** (optional)
   http://code.google.com/p/modwsgi

Installation
------------

1. Checkout sources from the GIT repository:

    `git clone https://github.com/djangoERPTeam/django-erp.git`

2. Copy and rename **djangoerp/settings/base.py.tmpl** to  **djangoerp/settings/base.py**.
 
3. Edit the **djangoerp/settings/base.py** content.

4. Initialize the database and all applications:

    `python manage syncdb`

5. Test the installation running the development web-server (http://localhost:8000 on your browser):

    `python manage runserver`
