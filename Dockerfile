FROM python:3.5

ENV CLOUDY_PORT=8000

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE ${CLOUDY_PORT}

CMD python manage.py runserver 0.0.0.0:${CLOUDY_PORT}
