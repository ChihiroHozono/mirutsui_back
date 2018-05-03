# グルナビのKeyID
import gurunavi_keyid
# HTTPリクエスト
import requests
import json
import mysql.connector
# 文字列を正規表現で置き換えれる
import re
# 現在時刻の取得
from datetime import datetime


# areacode_s（地域コード）を引数に入れるとその地域の
# レストランのshop_id,shop_name,口コミを取得してくれる
class Get_shop_id_name_comment:

	def __init__(self,areacode_s):
		# インスタンス変数
		self.areacode_s = areacode_s
		# 取得したデータの総数
		self.total_count = 0
		# 取得した口コミの総数
		self.total_comment = 0
		self.execution()


	# インスタンス化時に入れたareacode_s（地域コード）を元にその地域のレストランのデータを返す関数
	def return_shop_datas(self,offset_page=1):
		# レストラン検索用のAPI
		url= "https://api.gnavi.co.jp/RestSearchAPI/20150630/"

		# GET送信のパラメータ
		params={
		# グルナビのKeyID
	    "keyid":gurunavi_keyid.keyid,
	    # グルナビが東京に割り当てた地域コード
	    # "pref":"PREF13",
	    "areacode_s":self.areacode_s,
	    "format":"json",
	    # 一回のリクエスト得られるレスポンスの数の変更（最大で100）
	    "hit_per_page":100,
	    # 検索開始ページ位置
	    "offset_page":offset_page
		}

		responses = requests.get(url,params=params)
		print(responses.headers)

		# json形式の店舗データ集まり
		shop_datas = responses.json()



		return shop_datas


	# レストランの名前をキーにIDを値に入れて返す関数
	def return_shop_id_name(self,shop_datas=1):

		# index番号を表すリストの作成
		indexes = range(len(shop_datas["rest"]))

		shops_id_name ={}
		for index in indexes:
			# レストランの一つ一つのid
			shop_name = shop_datas["rest"][index]['name']
			shop_id = shop_datas["rest"][index]['id']

			# shopをリストに追加
			shops_id_name[shop_id] = shop_name

		return shops_id_name



	# shops_id_nameを元にそれぞれのレストランの口コミのデータを取得し保存
	def rerutn_comment_data(self,shops_id_name):
		# 口コミ検索用のURL
		url = "https://api.gnavi.co.jp/PhotoSearchAPI/20150630/"
		# １つ1つのレストランの口コミのデータを取り出す
		percent = 0

		for shop_id,shop_name in shops_id_name.items():
			print("現在のページの"+str(percent)+"%が完了しました")
			params ={
			"keyid":gurunavi_keyid.keyid,
			"format":"json",
			"id":shop_id,
			"shop_name":shop_name,
			"hit_per_page":50
			}

			# １つのお店のレストランの複数の口コミデータが入ってる
			# レスポンスをJSONとして取得
			response = requests.get(url,params=params).json()

			# 口コミの件数
			comment_count = response['response']['total_hit_count']
			# 取得した口コミの件数をtotal_commentに足す
			self.total_count += comment_count

			if(comment_count == 0):
				pass
			# レビュー数が０以外の時ー＞commentを取得しshop_id,shop_name,comment,
			else:
				for index in range(comment_count):
					if(index <= 49):
							index= str(index)
							comment = response['response'][index]['photo']['comment']

							# データベースに接続し、shop_id,shop_name,shop_dataを保存する関数
							self.save_to_databse(shop_id,shop_name,comment)
					else:
						break
			percent += 1


	# データベースに接続し、shop_id,shop_name,shop_data,createdを保存する関数
	def save_to_databse(self,shop_id,shop_name,comment):
		# comment(口コミ)を正規化
		comment = re.sub("'|\"","",comment)

		# 現在時刻の取得
		now_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		# データベースに接続
		conn = mysql.connector.connect(
		user='root',
		password='',
		host='localhost',
		database='mirutsui')

		# カーソル
		cur = conn.cursor()
		SQL = f"INSERT INTO `tabelog_comments` SET `shop_id`=\"{shop_id}\",`shop_name`=\"{shop_name}\",`comment`=\"{comment}\",`created`=\"{now_date}\""
		cur.execute(SQL)
		conn.commit()
		cur.close()
		conn.close()



	# 全ての関数を実行する関数
	def execution(self):
		# インスタンス化時に入れたareacode_s（地域コード）を元にその地域のレストランのデータを返す関数

		# json形式の店舗データ集まり
		shop_datas = self.return_shop_datas()
		# レストランのデータの数を表示

		print("レストランの総数は" + shop_datas['total_hit_count'] + "件")
		print("現在取得中のページは" + shop_datas['page_offset'])

		# shop_datasから{shop_id:shop_name,.....}のdictionaryを作成
		shops_id_name = self.return_shop_id_name(shop_datas)
		#shop_id＿nameidからそれぞれのレストランの口コミのデータを取得し保存
		self.rerutn_comment_data(shops_id_name)
		# 取得したデータの総数を足す
		self.total_count +=100


		# レストランのデータの件数（total_hit_count）が一回に取得できるレストランデータの最大数（100）を超えた場合と1000件以上データがある場合
		# 取得するページ
		page = 2
		while(int(shop_datas['total_hit_count']) // 100 >= int(shop_datas['page_offset']) and page <=10):
			# ２ページ目のデータを拾ってくる
			shop_datas = self.return_shop_datas(page)

			print("レストランの総数は" + shop_datas['total_hit_count'] + "件です")
			print("現在取得中のページは" + shop_datas['page_offset'])
			print("現在取得したデータの総数は" + str(self.total_count))
			# shop_datasから{shop_id:shop_name,.....}のdictionaryを作成
			shops_id_name = self.return_shop_id_name(shop_datas)
			#shop_id＿nameidからそれぞれのレストランの口コミのデータを取得し保存
			self.rerutn_comment_data(shops_id_name)
			page +=1
			# 取得したデータの総数を足す
			self.total_count +=100




areacodes = ['AREAS3446']


for i in areacodes:
	Get_shop_id_name_comment(i)
	del areacodes[0]
	print(areacodes)








# pref_code(都道府県を表すコード)からareacode_sを表示
# def serch_areacode_s(pref_code):
# 	url= "https://api.gnavi.co.jp/master/GAreaSmallSearchAPI/20150630/"
# 	params={
# 	# グルナビのKeyID
# 	"keyid":gurunavi_keyid.keyid,
# 	"format":"json",
# 	}

# 	response = requests.get(url,params).json()
# 	print(response)
# 	for data in response['garea_small']:
# 		if(data['pref']['pref_code'] == pref_code):
# 			print(data['areacode_s'])

# serch_areacode_s('PREF13')

