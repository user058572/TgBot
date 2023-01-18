from Dicts import mentors_dict

import  httplib2
import apiclient.discovery
from oauth2client.service_account import  ServiceAccountCredentials

main_dict = {}


CREDENTIALS_FILE = 'creds.json'
spreadsheet_id = '1Nz_VX7fYU2O_TuM2XtmIRHlvmJofUkD5BnR5tkyw5so'
spreadsheet_id2 = '1wS0KsOqhX6mf-pPqiisWVaB3hKaiKtj8QwiQnLbJPR8'
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
 ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)
list = []
for i in mentors_dict:
    list.append(mentors_dict[i])

results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": "Лист2!A1:A30",
                 "majorDimension": "COLUMNS",
                 "values": [list]},
            ]
        }).execute()