## @package dataBaseAdpr
# Data Base implementation using Google Drive API
# @author Hugo Zepeda

## Librarys
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
    ## Data Base class
    # @class dataBaseAdpr 
    # @brief This class handles the update of the data base in Google Drive

    def __init__(self):
        ## @fn __init__ 
        # @brief  Class constructor in charge of autentication process for the Google Drive API
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                print('Taking credentials')
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                print('Creating credentials')
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
                print('Credentials safe for next run')
        self.drive_service = build('drive', 'v3', credentials=creds)
        
        '''
        ###TESTING BELOW###
        searchKey = 'OCHL'
        pathFile = 'jsonFolder/folderIds.json'
        folderID = self.keySearchValue(searchKey,pathFile)
        fileName = 'dbBITC_USDT_' + searchKey + '.json'
        pathFile = 'jsonFolder/' + fileName
        self.createUpdateFile(fileName, pathFile, folderID)
        self.downloadFiles()
        '''

    def updateFiles(self):
        ## @fn updateFiles 
        # @brief public method which handles the update of all the files to the data base on the cloud
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
        ## @fn downloadFiles 
        # @brief public method which handles the download of all the files to the local data base of the developer
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
        ## @fn createUpdateFile 
        # @brief public method for the creation of a new file
        # @param f_nameFile File name to be created on the Drive cloud
        # @param f_pathFile Local path of the file to be upload
        # @param f_folderID Previously known folderID where the file is to be located 
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
        ## @fn keySearchValue 
        # @brief public method to look up for a folderID
        # @param f_searchKeys Looking up key, which sets to the data look
        # @param f_pathFile Local path of the file folderIds.json
        # @return folderID  folderID on the cloud
        with open(f_pathFile) as dictIds:
            dictIds = json.load(dictIds)
            for key in dictIds: 
                folderID = self.__keySearch(f_searchKeys, dictIds[key])
                return folderID

    
    def __keySearch(self, f_searchKeys, f_dictIds):
        ## @fn keySearchValue 
        # @brief private method to do recursion on a dictionary
        # @param f_searchKeys Looked up key
        # @param f_dictIds Provided dictionary
        # @return f_dictIds[key] returns the value of the search key 
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