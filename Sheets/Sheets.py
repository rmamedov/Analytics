import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = 'Analytics-fa8d613c7bc3.json' #файл с нашим ключем. А сам ключ нужно складывать туда, где лежит сам файл с программой.

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                  'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

spreadsheet = '107nr2V9WYXAQ3Ah3w584ltaxcnrno1Trdk8tB2Ntysg'
results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet, body = {
  "requests": [

    # Задать ширину столбца A: 317 пикселей
    {
      "updateDimensionProperties": {
        "range": {
          "sheetId": 0,
          "dimension": "COLUMNS",  # COLUMNS - потому что столбец
          "startIndex": 0,         # Столбцы нумеруются с нуля
          "endIndex": 1            # startIndex берётся включительно, endIndex - НЕ включительно,
                                   # т.е. размер будет применён к столбцам в диапазоне [0,1), т.е. только к столбцу A
        },
        "properties": {
          "pixelSize": 317     # размер в пикселях
        },
        "fields": "pixelSize"  # нужно задать только pixelSize и не трогать другие параметры столбца
      }
    },

    # Задать ширину столбца B: 200 пикселей
    {
      "updateDimensionProperties": {
        "range": {
          "sheetId": 0,
          "dimension": "COLUMNS",
          "startIndex": 1,
          "endIndex": 2
        },
        "properties": {
          "pixelSize": 200
        },
        "fields": "pixelSize"
      }
    },

    # Задать ширину столбцов C и D: 165 пикселей
    {
      "updateDimensionProperties": {
        "range": {
          "sheetId": 0,
          "dimension": "COLUMNS",
          "startIndex": 2,
          "endIndex": 4
        },
        "properties": {
          "pixelSize": 165
        },
        "fields": "pixelSize"
      }
    },

    # Задать ширину столбца E: 100 пикселей
    {
      "updateDimensionProperties": {
        "range": {
          "sheetId": 0,
          "dimension": "COLUMNS",
          "startIndex": 4,
          "endIndex": 5
        },
        "properties": {
          "pixelSize": 100
        },
        "fields": "pixelSize"
      }
    }
  ]
}).execute()

print ('заебись')
