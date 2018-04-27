# Twitterの様々なkeyが入っている
import keys
import json
import numpy as np
from requests_oauthlib import OAuth1Session
from datetime import datetime
import mysql.connector
from pprint import pprint



conn = mysql.connector.connect(
        user='root',
        password='',
        host='localhost',
        database='mirutsui')
cur = conn.cursor()


twitter = OAuth1Session(keys.CK,keys.CS,keys.AT,keys.AS)
url = "https://api.twitter.com/1.1/search/tweets.json"
keyword = "geocode:35.658517,139.701334,0.5km"
# get送信に使うパラメータ
params = {'q' : keyword, 'count' : 10}
req = twitter.get(url, params = params)


# HTTPレスポンスを引数にデータベースに保存する関数
if req.status_code == 200:
    search_timeline = json.loads(req.text)
    for tweet in search_timeline['statuses']:
        data = {}
        data['tw_created_at'] = str(datetime.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))  
        data['tweet_id'] = tweet['id']
        # Python内でもエスケープシーケンスか効くので\\を二回使うで文字列を無効化
        data['text'] = tweet['text'].replace("'","")
        if(tweet['truncated'] == False):
            data['truncated'] = 0
        else:
            data['truncated'] = 1
        data['user_id'] = tweet['user']['id']
        data['user_name'] = tweet['user']['name'].replace("'","\\'")
        data['screen_name'] = tweet['user']['screen_name']
        data['location'] = tweet['user']['location'].replace("'","\\'")
        data['description'] = tweet['user']['description'].replace("'","\\'")
        if(tweet['user']['protected']==False):
            data['protected'] =  0
        else:
            data['protected'] = 1
        data['followers_count'] = tweet['user']['followers_count']
        data['friends_count'] = tweet['user']['friends_count']
        if(tweet['user']['geo_enabled'] == False):
            data['geo_enabled'] = 0
        else:
            data['geo_enabled'] = 1
        data['statuses_count'] = tweet['user']['statuses_count']
        data['user_lang'] = tweet['user']['lang']
        data['profile_image_url_https'] = tweet['user']['profile_image_url_https']
        try:
            data['lat'] = tweet['geo']['coordinates'][0]
            data['lng'] = tweet['geo']['coordinates'][1]
        except:
            data['lat'] = 0
            data['lng'] = 0

        # 配列だと同時に計算しやすい
		#ndarrayを入れるリスト
        ndarray = []
		#緯度経度を取得しndarrayに変換
        try:
            for i in tweet['place']['bounding_box']['coordinates'][0]:
                ndarray.append(np.array(i))
    			#４つの位置情報から中心地を求める
            geo = ((ndarray[0] + ndarray[1] +ndarray[2] + ndarray[3])/4).tolist()
            data['pol2lat'] = geo[1]
            data['pol2lng'] = geo[0]
            data['tweet_lang'] =tweet['lang']
        except:
            data['pol2lat'] = 0
            data['pol2lng'] = 0

        data['tweet_lang'] =tweet['lang']
        data['created'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


		#SQL文の作成
        SQL = 'INSERT INTO `tweet_data` SET '
        for key in data.keys():
            if(type(data[key]) ==int or type(data[key]) == float):
                SQL += "`{}`= {},".format(key,data[key])
            # 文の終わりの時の動作
            elif(key == 'created'):
                 SQL += "`{}`= '{}';".format(key,data[key])
            else:
                SQL += "`{}`= '{}',".format(key,data[key])
        print()
        print(SQL)
        cur = conn.cursor()
        cur.execute(SQL)
        conn.commit()

        max_id= int(tweet['id'])
        print(max_id)

# エラーだった時の処理
else:
    print("ERROR: %d" % req.status_code)





cur.close()
conn.close()

