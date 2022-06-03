# flask-weather-application
A simple Flask application tells you your geolocation and the weather there based on some public APIs.

### How to run ?
clone the repo to your local machine and cd into it.
Make sure you have Docker installed on your machine, then run the following command:

`docker build -t flask-app .`

`docker run -p 5000:5000 flask-app`

and the applcation should be running on the link showed in your Terminal on port 5000.
Note that the image might take some time to build.
