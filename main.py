
import logging

from flask import Flask, render_template, request, redirect

import pickle
import os.path
from google_auth_oauthlib import flow
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.appengine.api import users
from google.appengine.ext import ndb

import google.auth.transport.requests

# Needed so that the fetch_token call doesn't blow up.
# See 
# https://stackoverflow.com/questions/41246976/
# getting-chunkedencodingerror-connection-broken-incompleteread
from requests_toolbelt.adapters import appengine
appengine.monkeypatch()

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    # 'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
]

SAMPLE_RANGE_NAME = 'Actions!A1:D5'
SAMPLE_SPREADSHEET_ID = '1-Od5KTd5jsUSZUphweUUPf4Eu5A1uVucNi25-CHrq_k'

app = Flask(__name__)


redirect_uri = "http://localhost:8080/login/callback"
login_flow = flow.Flow.from_client_secrets_file('./credentials.json',
    redirect_uri=redirect_uri,
    scopes=SCOPES)

class GoogleOauthUser(ndb.Model):
    user_id = ndb.StringProperty()
    google_creds = ndb.StringProperty()

    @classmethod
    def get_by_user(cls, user):
        return cls.query().filter(cls.user_id == user.user_id()).get()

@app.route("/")
def my_main():
    user = users.get_current_user()
    my_user = GoogleOauthUser.get_by_user(user)
    if my_user == None or my_user.google_creds == None:
        auth_url, _ = login_flow.authorization_url(prompt='consent')
        return redirect(auth_url)

    creds = pickle.loads(my_user.google_creds)

    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    return_val = ''
    for item in items:
        return_val += '{0} ({1})'.format(item['name'], item['id'])
    return return_val

    # Uncomment to mess around with Google Sheets.
    #
    # service = build('sheets', 'v4', credentials=creds)
    # sheet = service.spreadsheets()
    # result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #                             range=SAMPLE_RANGE_NAME).execute()
    # values = result.get('values', [])

    # if not values:
    #     return 'No data found'
    # else:
    #     return_val = 'What, What'
    #     for row in values:
    #         # Print columns A and E, which correspond to indices 0 and 4.
    #         return_val += '%s, %s' % (row[0], row[1])
    #     return return_val


@app.route("/login/callback")
def loginCallback():
    user_code = request.args.get('code')
    login_flow.fetch_token(code=user_code)
    creds = login_flow.credentials
    pickled_creds = pickle.dumps(creds)

    user = users.get_current_user()
    new_user = GoogleOauthUser(user_id=user.user_id(),
        google_creds=pickled_creds)
    new_user.put()
    return redirect("/")



