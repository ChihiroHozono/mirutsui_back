# 地域のデータを取得する

import json
from pprint import pprint
import gurunavi_keyid
import requests

def serch_pref_code():
	url = "https://api.gnavi.co.jp/master/PrefSearchAPI/20150630/"
	params={
	# グルナビのKeyID
	"keyid":gurunavi_keyid.keyid,
	"format":"json",
	}

	response = requests.get(url,params).json()
	pprint(response)




# pref_code(都道府県を表すコード)からareacode_sを表示
def serch_areacode_s(pref_code):
	url= "https://api.gnavi.co.jp/master/GAreaSmallSearchAPI/20150630/"
	params={
	# グルナビのKeyID
	"keyid":gurunavi_keyid.keyid,
	"format":"json",
	}

	response = requests.get(url,params).json()
	pprint(response)
	for data in response['garea_small']:
		if(data['pref']['pref_code'] == pref_code):
			pprint(data['areacode_s'])


# serch_pref_code()
serch_areacode_s("PREF27")


