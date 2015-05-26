Tornado (with Websockets and Django) on Red Hat's OpenShift PaaS
=====================================================

Tornado running on OpenShift with Websocket and Django support.

This git repository is a sample application to help you get started
using Tornado with Django and Websocket support on Red Hat's OpenShift PaaS.

Python Packages
---------------

This application uses **Python2.7** and requires the following python packages: (requirements.txt)

    backports.ssl-match-hostname==3.4.0.2
    certifi==14.5.14
    Django==1.7.3
    tornado==4.0.2


Steps to get Tornado, Django and Websockets running on OpenShift
-----------------------------------------

Create an account at http://openshift.redhat.com/

Create a namespace, if you haven't already done so:

    rhc domain create -n <yournamespace>

Create a python-2.7 application:

    rhc app create dtornado python-2.7
    
Add the database cartridge (Choose one):

    rhc add-cartridge mysql-5.5 --app dtornado

    OR

    rhc add-cartridge postgresql-9.2 --app dtornado


Add this `django-tornado-websockets-openshift` repository:

    cd dtornado
    git remote add upstream -m master https://github.com/awwong1/django-tornado-websockets-openshift.git
    git pull -s recursive -X theirs upstream master
    
Then push the repo to OpenShift

    git push

That's it, you can now view your application

    http://dtornado-$yournamespace.rhcloud.com
    
Be sure to create your super user to access the admin portion of the website.

    rhc ssh dtornado
    python app-root/repo/manage.py createsuperuser

To view your application locally in a development environment,
simply run app.py and navigate to localhost:8080 within a web browser.

    python manage.py collectstatic
    python app.py
    
