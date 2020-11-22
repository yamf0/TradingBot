###LIBRARYS###
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload
import json
import ast

SCOPES = ['https://www.googleapis.com/auth/drive']

class dataBaseAdpr():
    """
        This class will upload and download files from Drive
    """  
    # If modifying these scopes, delete the file token.pickle.

    def __init__(self):
        """
            Authenticate Login for first time, then ist automatically
        """   
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                print('Taking credentials')
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                print('Creating credentials')
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        self.drive_service = build('drive', 'v3', credentials=creds)

        ###TESTING BELOW###
        '''
        searchKey = 'OCHL'
        pathFile = 'jsonFolder/folderIds.json'
        folderID = self.keySearchValue(searchKey,pathFile)
        fileName = 'dbBITC_USDT_' + searchKey + '.json'
        pathFile = 'jsonFolder/' + fileName
        self.createUpdateFile(fileName, pathFile, folderID)
        
        self.downloadFiles()
        '''

    def updateFiles(self):
        with open('jsonFolder/documentIDs.json','r') as f:
            dictIds = json.load(f)
            for key in dictIds:
                pathFile = 'jsonFolder/' + key
                media = MediaFileUpload(pathFile,
                                        mimetype='application/json',
                                        resumable=True)
                file = self.drive_service.files().update(
                                                    media_body=media,
                                                    fileId=dictIds[key]).execute()

    def downloadFiles(self):
        with open('jsonFolder/documentIDs.json','r') as f:
            dictIds = json.load(f)
            for key in dictIds:
                pathFile = 'jsonFolder/' + key
                content = self.drive_service.files().get_media(fileId=dictIds[key]).execute()
                content =  content.decode('utf-8')
                content = ast.literal_eval(content)
                with open(pathFile,'w') as f:
                    json.dump(content,f)
    '''
    def updateFolderIds(self):
        page_token = None
        while True:
            response = drive_service.files().list(q="mimeType='application/vnd.google-apps.folder'",
                                                spaces='drive',
                                                fields='nextPageToken, files(id, name)',
                                                pageToken=page_token).execute()
            for file in response.get('files', []):
                # Process change
                print ('Found file: %s (%s)' % (file.get('name'), file.get('id')))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
    '''
    def createUpdateFile(self, f_nameFile, f_pathFile, f_folderID):
        file_metadata = {
            'name': f_nameFile,
            'parents': [f_folderID]
        }
        media = MediaFileUpload(f_pathFile,
                                mimetype='application/json',
                                resumable=True)
        file = self.drive_service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()        
        newID = file.get('id')
        newKey = {f_nameFile : newID}
        with open('jsonFolder/documentIDs.json','r') as f:
            dictIds = json.load(f)
            dictIds.update(newKey)
        with open('jsonFolder/documentIDs.json','w') as f:
            json.dump(dictIds,f)

    def keySearchValue(self, f_searchKeys, f_pathFile):
        with open(f_pathFile) as dictIds:
            dictIds = json.load(dictIds)
            for key in dictIds: 
                value = self.keySearch(f_searchKeys, dictIds[key])
                return value

    
    def keySearch(self, f_searchKeys, f_dictIds):
        for key in f_dictIds:
            if key != f_searchKeys:
                if isinstance(f_dictIds[key],dict):
                    return self.keySearch(f_searchKeys, f_dictIds[key])
                continue
            else:
                return (f_dictIds[key])

def main():
    workAround = dataBaseAdpr()


if __name__ == '__main__':
    main()