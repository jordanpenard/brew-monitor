FROM python:3.9

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install stuff
RUN apt-get update
RUN apt-get install -y apache2 apache2-utils git sudo
RUN apt-get install -y libapache2-mod-wsgi-py3
RUN pip3 install --upgrade pip
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

# port where the Django app runs
EXPOSE 80

# Apache setup
COPY ./site-config.conf /etc/apache2/sites-available/000-default.conf

# start server
CMD ["apache2ctl", "-DFOREGROUND"]
