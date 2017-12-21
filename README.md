# Cloudy McCloudface

Das Team PressAnyKey macht es sich zur Aufgabe eine Cloud-Anwendung auf Basis von Python und Django zu entwickeln.
Die Cloud wird mehrbenutzerfähig sein mit einer Datenbank im Backend. Der Nutzer soll Dateien und Dokumente hoch- und runterladen können. Text-Dokumente werden verschlagwortet und können mit zusätzlichen Informationen wie z.B. Quellenangaben versehen werden. Die Inhalte sowie die Dateinamen sind über die Suche wieder auffindbar. Einfache Textdateien kann man bearbeiten und Bilddateien kann man sich direkt anschauen.

## Set up

This readme describes how to set up this development environment using Docker or Virtualenv. Both ways are supported by PyCharm.

### Set up container

Choose between Docker and virtualenv.

#### Using Docker

- Install Docker:
  https://docs.docker.com/engine/installation/
- Install docker-compose:
  https://docs.docker.com/compose/install/
- Set permissions to keep access on docker created items:
  `bash set-permissions.sh`

#### Using virtualenv

- Install virtualenv for python:
  ```
  apt install python3-pip
  pip3 install virtualenv==15.1.0
  ```

### Set up development environment

- Get source:
  ```
  git clone git@gitlab.beuth-hochschule.de:pressanykey/cloudy-mccloudface.git
  cd cloudy-mccloudface
  ```

#### Using Docker

No further steps needed.

#### Using virtualenv
 
- Set up virtualenv:
  ```
  virtualenv -p /usr/bin/python3.5 venv
  ```

### Install dependencies and build assets

#### Using Docker

```
docker-compose run django npm install
docker-compose run django npm install gulp -g
docker-compose run django gulp build
```

#### Using Virtualenv

```
npm install
npm install gulp -g
gulp build
```

## Run environment

Do the steps below and open the project in your web server: http://localhost:8000/.

### Using Docker

- `docker-compose run django python manage.py migrate`
- `docker-compose up -d` (the first run may take a while as the image gets build)

#### Using virtualenv

  ```
  source venv/bin/activate
  python manage.py migrate
  python manage.py runserver 8000
  ```

### PyCharm

If you're using PyCharm, you need to do these steps.

- Checkout from Git Repo or open already existing project folder.
- Set python interpreter to use virtualenv or docker-compose.
- Set a _Run/Debug-Configuration_ for _Django server_ using this interpreter
    - If using docker-compose: Set the _Host_ to _0.0.0.0_ to be able to access the Django server from outside the docker container.

## FAQ

- If you get permission problems when using Docker:
  - run `bash set-permissions.sh` again
  
  