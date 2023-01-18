
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


def users(row, range, regim, values=[]):
    if regim == "read":
        values = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="Лист1!" + range,
            majorDimension=row
        ).execute()
        if "values" in values:
            num = values["values"]
            return num
    else:
        results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": "Лист1!" + range,
                 "majorDimension": row,
                 "values": values},
            ]
        }).execute()


def olimpiad(row, range, regim, values=[]):
    if regim == "read":
        values = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id2,
            range="Лист1!" + range,
            majorDimension=row
        ).execute()
        if "values" in values:
            num = values["values"]
            return num
    else:
        results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id2, body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": "Лист1!" + range,
                 "majorDimension": row,
                 "values": values},
            ]
        }).execute


def olimpiadRaiting(row, range, regim, values=[]):
    if regim == "read":
        values = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id2,
            range="Лист2!" + range,
            majorDimension=row
        ).execute()
        if "values" in values:
            num = values["values"]
            return num
    else:
        results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id2, body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": "Лист2!" + range,
                 "majorDimension": row,
                 "values": values},
            ]
        }).execute()


def kolvoStrok(nameOfTable):
    with open(nameOfTable, 'r', encoding='utf-8') as file:
        num = int(file.readline())
    return num

def plusStroka(nameOfTable):
    with open(nameOfTable, 'r', encoding='utf-8') as file:
        num = int(file.readline())
    with open(nameOfTable, 'w', encoding='utf-8') as file:
        file.write(str(num + 1))


results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id2, body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": "Лист1!A2:C2",
                 "values": [[1, 2, 3]]},
            ]
        }).execute()