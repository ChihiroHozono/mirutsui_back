# 地域のデータを取得する

import json
from pprint import pprint
import gurunavi_keyid
import requests

def return_pref_name_and_code():
	url = "https://api.gnavi.co.jp/master/PrefSearchAPI/20150630/"
	params={
	# グルナビのKeyID
	"keyid":gurunavi_keyid.keyid,
	"format":"json",
	}

	response = requests.get(url,params).json()['pref']
	pprint(response)
	# pref_code（都道府県のコード）を辞書で返す
	pref_dic ={}
	# 要素の数でイテレータ？を作成
	for i in range(len(response)):
		pref_dic[response[i]['pref_name']] = response[i]['pref_code']
	return pref_dic




# pref_code(都道府県を表すコード)からareacode_sを表示
def serch_areacode_s(pref_code):
	url= "https://api.gnavi.co.jp/master/GAreaSmallSearchAPI/20150630/"
	params={
	# グルナビのKeyID
	"keyid":gurunavi_keyid.keyid,
	"format":"json",
	}

	response = requests.get(url,params).json()
	# areacode_sリスト
	list_areacode_s=[]
	for data in response['garea_small']:
		if(data['pref']['pref_code'] == pref_code):
			list_areacode_s.append(data['areacode_s'])
	return list_areacode_s




serch_areacode_s('PREF24')

