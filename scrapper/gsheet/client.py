import json
from re import S
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from pprint import pprint
from google.oauth2 import service_account



def ToCellData(cell) -> dict[str, dict[str, str]]:
    return {'userEnteredValue': {'stringValue': str(cell)}}


def ToRowData(row) -> dict[str, list[dict[str, dict[str, str]]]]:
    return {'values': list(map(ToCellData, row))}


class Sheet:
    def __init__(self, sheet) -> None:
        properties = sheet.get('properties')
        self.id = properties.get('sheetId')
        self.title = properties.get('title')
        self.index = properties.get('index')
        gridProperties = properties.get('gridProperties')
        self.rows = gridProperties.get('rowCount')
        self.cols = gridProperties.get('columnCount')


class Spreadsheet:
    def __init__(self, spreadsheet, parent) -> None:
        self.aiogoogle_api = parent.aiogoogle_api
        self.spreadsheet_service = parent.spreadsheet_service
        self.sheep_api_service = parent.sheep_api_service
        
        self.id = spreadsheet.get('spreadsheetId')
        self.url = spreadsheet.get('spreadsheetUrl')
        self.sheets = [Sheet(s) for s in spreadsheet.get('sheets')]
        self.sheets = {s.title: s for s in self.sheets}

    def sheet_by_title(self, title):
        return self.sheets[title]
    
    async def get_values(self, range):
        resp = await self.aiogoogle_api.as_service_account(self.spreadsheet_service.values.get(spreadsheetId=self.id, range=range))
        return resp.get('values', [])
    
    async def get_values_batch(self, ranges):
        resp = await self.aiogoogle_api.as_service_account(
            self.spreadsheet_service.values.batchGet(spreadsheetId=self.id, ranges=ranges)
        )
        return [r.get('values', []) for r in resp.get('valueRanges')]

    async def append_values(self, range, values):
        valueRange = {
            'range': range,
            'values': values
        }
        await self.aiogoogle_api.as_service_account(self.spreadsheet_service.values.append(spreadsheetId=self.id, range=range, valueInputOption='USER_ENTERED', json=valueRange))

    async def update_values_batch(self, ranges, values):
        body = {
            "valueInputOption": "USER_ENTERED",
            "data": [{"range": r, "values": v} for r, v in zip(ranges, values)]
        }
        req = self.spreadsheet_service.values.batchUpdate(spreadsheetId=self.id, json=body)
        await self.aiogoogle_api.as_service_account(req)

    async def update_values(self, id, Range, InsertValues):
        body = {'values': InsertValues}
        await self.aiogoogle_api.as_service_account(self.spreadsheet_service.values.update(spreadsheetId=self.id, range=Range, valueInputOption='USER_ENTERED', json=body))
        


class SheetApiClient:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        # self._sheetService = None
        self._spreadsheet = None
        self.aiogoogle_api = None

    async def loadasyncsheetservice(self, serviceAccountFile):
        with open(serviceAccountFile, "r") as read_file:
            credfile = json.load(read_file)
            asynccreds = None
            asynccreds = ServiceAccountCreds(scopes=self.SCOPES, **credfile)
            async with Aiogoogle(service_account_creds=asynccreds) as aiogoogle:
                self.sheep_api_service = await aiogoogle.discover("sheets", "v4")
            self.spreadsheet_service = self.sheep_api_service.spreadsheets
            self.aiogoogle_api = aiogoogle
        
    async def get_shreadsheet(self, id):
        resp = await self.aiogoogle_api.as_service_account(self.spreadsheet_service.get(spreadsheetId=id, includeGridData=False))
        return Spreadsheet(resp, self)
        
    async def get_values(self, id, range):
        resp = await self.aiogoogle_api.as_service_account(self.spreadsheet_service.values.get(spreadsheetId=id, range=range))
        return resp.get('values', [])
    
    async def get_values_batch(self, id, ranges):
        resp = await self.aiogoogle_api.as_service_account(
            self.spreadsheet_service.values.batchGet(spreadsheetId=id, ranges=ranges)
        )
        return [r.get('values', []) for r in resp.get('valueRanges')]

    async def append_values(self, id, range, values):
        valueRange = {
            'range': range,
            'values': values
        }
        await self.aiogoogle_api.as_service_account(self.spreadsheet_service.values.append(spreadsheetId=id, range=range, valueInputOption='USER_ENTERED', json=valueRange))

    async def update_values_batch(self, id, ranges, values):
        body = {
            "valueInputOption": "USER_ENTERED",
            "data": [{"range": r, "values": v} for r, v in zip(ranges, values)]
        }
        req = self.spreadsheet_service.values.batchUpdate(spreadsheetId=id, json=body)
        await self.aiogoogle_api.as_service_account(req)

    async def update_values(self, id, Range, InsertValues):
        body = {'values': InsertValues}
        await self.aiogoogle_api.as_service_account(self.spreadsheet_service.values.update(spreadsheetId=id, range=Range, valueInputOption='USER_ENTERED', json=body))
