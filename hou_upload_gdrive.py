import pickle
import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request


def Create_Service(client_secret_file, api_name, api_version, *scopes):
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]

    cred = None

    pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        print(API_SERVICE_NAME, 'service created successfully')
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None

dir_geo = 'D:/Rebelway Courses/Python for Production/Week 3/Assignment/'
name_geo = 'output.abc'
secret_file = hou.pwd().parm("cred_file").evalAsString()
gdriv_fid = hou.pwd().parm("g_folder_id").evalAsString()
full_path = dir_geo+name_geo
print(full_path)

CLIENT_SECRET_FILE = secret_file
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

folder_id = gdriv_fid
file_name = name_geo
mime_type = 'application/octet-stream'

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

if __name__ == '__main__':
    file_metadata = {'name': file_name, 'parents' : [folder_id]}
    media = MediaFileUpload(full_path, mime_type)

    service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(file_name," uploaded to GDrive folder ",folder_id," successfully!")
