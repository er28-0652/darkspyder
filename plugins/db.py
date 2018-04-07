import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class PandasSpreadSheet:
    def __init__(self, sp):
        self.sp = sp
        self.wks = None
    
    def open(self, sheet_name):
        self.wks = self.sp.worksheet(sheet_name)

    def read(self):  
        data = self.wks.get_all_values()
        return pd.DataFrame(data[1:], columns=data[0])

    def append(self, data):
        for value in data.values:
            self.wks.append_row(list(value))


def gen_spreadsheet_client(key_file):
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file, scope)
    gc = gspread.authorize(credentials)
    def open(space_key):
        space = gc.open_by_key(space_key)
        return PandasSpreadSheet(space)
    return open
