FROM python:3.5

# default port for django server
ENV CLOUDY_PORT=8000

WORKDIR /usr/src/app

# install npm (and nodejs)
RUN apt-get update \
    && apt-get install -y apt-transport-https lsb-release \
    && curl -s https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - \
    && echo 'deb https://deb.nodesource.com/node_8.x jessie main' > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# install gulp
RUN npm install -g gulp

# install required pip packages
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# make the port available
EXPOSE ${CLOUDY_PORT}

# run django
CMD python manage.py runserver 0.0.0.0:${CLOUDY_PORT}
