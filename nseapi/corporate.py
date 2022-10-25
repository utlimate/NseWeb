import io
import zipfile
import pandas as pd
import ast
import datetime
import requests

class Corporate:
    def __init__(self, data: dict) -> None:
        for k, v in data.items():
            setattr(self, k.replace(" ", "").lower(), v)


class FinTaxonomy:
    def __init__(self, url: str = None, file_name: str = None, sheet_name: str = None) -> None:
        self.url = url or 'https://www.bseindia.com/downloads1/Fin_Taxonomy.zip'
        self.file_name = file_name or 'Fin_Taxonomy/Ind AS Taxonomy 2020-03-31/Ind AS Taxonomy-2020-03-31.xlsx'
        self.sheet_name = sheet_name or 'Label'
        self._df = None
        
    @property
    def dataframe(self):
        return self._df    
        
    def init(self):
        """
        Download a ZIP file and extract its contents in memory
        yields (filename, file-like object) pairs
        """
        
        HEADER = {'user-agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
        response = requests.get(self.url, headers=HEADER, stream=True)
        with zipfile.ZipFile(io.BytesIO(response.content)) as thezip:
            if self.file_name in thezip.namelist():
                zipinfo = thezip.getinfo(self.file_name)
                with thezip.open(zipinfo) as thefile:
                    self._df = pd.read_excel(thefile, sheet_name=self.sheet_name)
        
        self._df['lower_name'] = self._df['name'].str.lower()
                    
    def find(self, ref: str):
        ref = ref.lower()
        result = self._df[self._df['lower_name'] == ref]['label']
        if len(result) == 1:
            return result.values[0]
        elif len(result) < 1:
            raise KeyError(f"Key: {ref} not found")
        else:
            raise ValueError(f"Key: {ref} more one result found - {str(result)}")
            


class Financial(object):
    def __init__(self, *args, **kwargs):
        for k , v in kwargs.items():
            if k == 'value':
                try:
                    try:
                        self[k] = ast.literal_eval(v)
                    except SyntaxError:
                        self[k] = datetime.strptime(v, "%Y-%m-%d")
                except ValueError:
                    self[k] = v
            else:
                self[k] = v
                # if 'date' == kwargs['id'][:4]:
                #     print(f"key: {kwargs['id']}, value: {kwargs['value']} - error type: {type(e)}, error: {e}")

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def pop(self, *args):
        return self.__dict__.pop(*args)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)


def get_financial(url: str):
    # res = session.get("https://www.nseindia.com", headers=HEADER)

    res_fin = session.get(url)
    financial = Financial()
    res_text = res_fin.text

    soup = BeautifulSoup(res_text, 'lxml')
    tag_list = soup.find_all()
    tag_result = []
    for tag in tag_list:
        try:
            tag_name = None
            if tag['contextref'] == 'OneD':
                tag_result.append(tag)
                tag_name = tag.name.split(":")[-1]
                if tag_name is not None:
                    financial[tag_name] = Financial(id=tag_name, desc=fin_taxonomy.find(tag_name), value=tag.text)

        except KeyError:
            pass
    return financial

c = Corporate({'sachin': 1, 'kahaan':2})
print(c)