import requests
from bs4 import BeautifulSoup
import zipfile, io
import pandas as pd
import ast


class FinTaxonomy:
    def __init__(self, url: str = None, file_name: str = None, sheet_name: str = None) -> None:
        self._df = pd.read_csv("Ind AS Taxonomy-2020-03-31 CSV.csv")
        
    @property
    def dataframe(self):
        return self._df    
        
    # def init(self):
    #     """
    #     Download a ZIP file and extract its contents in memory
    #     yields (filename, file-like object) pairs
    #     """
        
    #     HEADER = {'user-agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
    #     response = requests.get(self.url, headers=HEADER, stream=True)
    #     with zipfile.ZipFile(io.BytesIO(response.content)) as thezip:
    #         if self.file_name in thezip.namelist():
    #             zipinfo = thezip.getinfo(self.file_name)
    #             with thezip.open(zipinfo) as thefile:
    #                 self._df = pd.read_excel(thefile, sheet_name=self.sheet_name)
        
        # self._df['lower_name'] = self._df['name'].str.lower()
                    
    def find(self, ref: str, lower: bool = True):
        ref = ref.lower()
        result = self._df[self._df['lower_name'] == ref]['label']
        if len(result) == 1:
            return result.values[0]
        elif len(result) < 1:
            raise KeyError(f"Key: {ref} not found")
        else:
            raise ValueError(f"Key: {ref} more one result found - {str(result)}")
