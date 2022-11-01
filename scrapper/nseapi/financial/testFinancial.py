import ast
from datetime import datetime
import requests
import constants as const
import xml.etree.ElementTree as ET

session = requests.Session()
session.headers.update(const.HEADER)
HOMEPAGE = 'https://www.nseindia.com/'
res = session.get(HOMEPAGE)

# FINANCIAL_URL = 'https://www.nseindia.com/api/corporates-financial-results'
RELIANCE_QUATERLY = 'https://archives.nseindia.com/corporate/xbrl/INDAS_73302_495021_23072021080622_WEB.xml'
RELIANCE_ANNUAL = 'https://archives.nseindia.com/corporate/xbrl/INDAS_84064_651788_06052022083214_WEB.xml'


# SYMBOL = 'INFY'
# ISSUER = 'Infosys Limited'
# # PARAMS = {
# #     'index': 'equities',    #equities, sme, debt
# #     'symbol': SYMBOL,
# #     'period': 'Annual'
# # }

# PARAMS = {
#     'index': 'equities',    #equities, sme, debt
# }

# financial = session.get(FINANCIAL_URL, params=PARAMS)
# fin_data = financial.json()
# print(f"Total Results: {len(fin_data)}")

def parseXML(xmltext):
    # create element tree object
	tree = ET.fromstring(xmltext)
	# root = tree.getroot()

	# create empty list for news items
	result = {}
	for item in tree.findall(".//*[@contextRef='OneD']"):
		if item.tag.startswith("{http://www.bseindia.com/xbrl/fin/2020-03-31/in-bse-fin}"):
			key = item.tag.replace("{http://www.bseindia.com/xbrl/fin/2020-03-31/in-bse-fin}", '')
			
			value = item.text
			try:
				value = ast.literal_eval(value)
			# except SyntaxError:
			# 	try:
			# 		value = datetime.strptime(value, "%Y-%m-%d")
			# 	except ValueError:
			# 		pass
			# except ValueError:
			# 	pass
			except Exception as e:
				try:
					value = datetime.strptime(value, "%Y-%m-%d")
				except ValueError:
					if value == 'true' or value == 'false':
						value = ast.literal_eval(value.title())

			result[key] = value
		else:
			print('not')
	
	# return news items list
	return result


xml_res = session.get(RELIANCE_ANNUAL)
xml_res.text
finResultData = parseXML(xml_res.text)

print('test')
# from datetime import datetime

# def get_year_name(data: dict):
#         from_year = datetime.strptime(data['fromDate'], "%d-%b-%Y")
#         from_year = datetime.strftime(from_year, "%y%m")

#         to_year = datetime.strptime(data['toDate'], "%d-%b-%Y")
#         to_year = datetime.strftime(to_year, "%y%m")

#         return from_year + '_' + to_year

# results = {}

# for r in fin_data:
#     results[r['symbol']] = {}
#     results[r['symbol']][r['period']] = {}
#     results[r['symbol']][r['period']][get_year_name(r)] = {}
#     results[r['symbol']][r['period']][get_year_name(r)][r['consolidated']] = r



# def get_result(data: dict):
#     # result = None
#     result_couter = 0
#     try:
#         for k, v in data.items():
#             if isinstance(v, dict):
#                 get_result(v)
#             # else:
#             #     result = v
        
#         result_couter += 1
#         print(result_couter)
#             # yield result
#         # else:
#         #     yield data
#     except:
#         raise StopIteration()

# for r in get_result(results[SYMBOL]):
#     print(r)