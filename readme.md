TubeList - WebApplication for cooperative creating playlist for YouTube
=======================================================================

Aplikacja przystosowana do instalacji na serwerze OpenShift.com.

Wykorzystuje serwer Tornado do obsługi WebSocket oraz Framework Django 
do serwowania stron dynamicznych.

Wymagania
---------------

Aplikacja używa **Python2.7** i wymaga zainstalowanych poniższych pakietów: (requirements.txt)

    backports.ssl-match-hostname==3.4.0.2
    certifi==14.5.14
    Django==1.8
    tornado==4.0.2
    google-api-python-client


Uruchamianie lokalne
-----------------------------------------

Aby uruchomić aplikację w lokalnym środowisku, wystarczy uruchomić app.py

    $ python app.py

a następnie otworzyć w przeglądarce internetowej adres: 

    http://localhost:8080

Przy pierwszym uruchamianiu należy wykonać dodatkowo polecenia:

    $ python manage.py migrate
    $ python manage.py collectstatic
    
Działająca wersja
---------------------------------

Działająca wersja aplikacji dostępna jest pod adresem:

    http://tubelist-formatc.rhcloud.com/
