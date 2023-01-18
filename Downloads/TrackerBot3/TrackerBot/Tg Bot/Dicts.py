import  httplib2
import apiclient.discovery
from oauth2client.service_account import  ServiceAccountCredentials

main_dict = {}


CREDENTIALS_FILE = 'creds.json'
spreadsheet_id = '1Nz_VX7fYU2O_TuM2XtmIRHlvmJofUkD5BnR5tkyw5so'
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
 ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

participation_stage_dict = {
    'passed_registration': 'Прошёл регистрацию',
    'wrote_qualifying': 'Написал отборочный этап',
    'passed_final': 'Прошёл на заключительный этап',
    'took_final': 'Принял участие в финале(участник)',
    'final_prize_winner': 'Призёр финала(диплом 2 или 3 степени)',
    'winner_of_final': 'Победитель финала(диплом 1 степени',
}

mentors_dict = {

}

lessons_dict = {

}

def main2():
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="Лист2!A1:A30",
        majorDimension="COLUMNS"
    ).execute()
    values = values["values"][0]
    for i in range(len(values)):
        mentors_dict['mentor' + str(i + 1)] = values[i]

    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="Лист3!A1:A30",
        majorDimension="COLUMNS"
    ).execute()
    values = values["values"][0]
    for i in range(len(values)):
        lessons_dict['lesson' + str(i + 1)] = values[i]