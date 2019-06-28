# movie_api
A flask api that handles json files from a third party cinema api

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.
### Prerequisites
```
You will need to have Python with Virtualenv and Git installed on your machine.
This guide also assumes you are in a Windows environment.
```

### Installing

First clone the application code into any directory on your disk:
```
> cd /path/to/my/workspace/
> git clone https://github.com/sepira/movie_api.git
> cd movie_api
```
Create a virtual Python environment in a directory named venv, activate the virtualenv and install required dependencies using pip:
```
> virtualenv venv
> venv\Scripts\activate
(venv) > pip install -r requirements.txt
```
Now let’s set up the app for development and start it:
```
> python app.py
```
In your browser, open the URL http://localhost:8888/api/

## Running the tests

Tasks 1 - 4
```
For the fetch/ and movies/ commands just click on 'Try it out' and click 'Execute'
```
Task 5
```
Similar to /movies/<uuid>/schedule/ - do the same but uuid parameter is required
```
```
To use the show_date option, just copy the url of /movies/<uuid>/schedule/ paste in url browser and add ?show_date=<date> in the end.
```

