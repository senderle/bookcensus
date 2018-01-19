# Django Development with Docker

## Building and starting the container for the first time:

Run docker-compose up to start the Django server

`docker-compose up`

The default port is `8000`, visit `http://localhost:8000/`

## Running default migrations and creating a superuser account:

After you've run `docker-compose up`, for the first time, 
you'll need to run Django's default migrations and create 
a superuser account.

First open a new terminal window. The server process started
by `docker-compose up` must be running -- don't terminate it!
To run the migrations, use this command:

`docker-compose run web python manage.py migrate`

Then you can create a Django superuser:

`docker-compose run web python manage.py createsuperuser`

## Modifying your Django project and restarting the server:

After changing Django code, you may need to restart the 
server to test your changes. To do so, use this command:

`docker-compose restart`
