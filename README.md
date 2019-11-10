# Example of Google Oauth for Google Drive in Python on Appengine
This is a basic example of the Google Oauth flow in a web app
running on AppEngine.

It stores the user's access token in a User object and deals
with the first authentication flow. It does *not* deal with
token refreshes.

## Installing

- Create a python virtual environment for Python 2.7.
- Activate your virtualenv
- Setup your Application in the Google Cloud console and download
your application secrets file to a credentials.json in the top level
folder.
- Install dependencies using
```
(python-env)$ pip install -t lib -r requirements.txt
```
- Run using the AppEngine developer app server.
```
dev_appserver.py app.yaml
```
- When you navigate to localhost:8080 you should see the contents
of your Google Drive listed.



