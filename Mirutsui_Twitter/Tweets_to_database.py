# Twitterの様々なkeyが入っている
import keys
import json
import numpy as np
from requests_oauthlib import OAuth1Session
from datetime import datetime
import mysql.connector
from pprint import pprint
# プログラムを一時停止するために使う
import time


class Tweets_to_database:

    def __init__(self):
        # 古いツイートほどIDが小さいのでIDの大きさを比べ小さいと代入
        self.max_id =1000000000000000000000
        response = self.return_response()

        self.save_tweet(response)
        while(True):
            response = self.return_response(self.max_id)
            self.save_tweet(response)


    # get送信のレスポンスを返す
    # max_idを指定してツイートを取得できるようにする
    def return_response(self,max_id=None):
        twitter = OAuth1Session(keys.CK,keys.CS,keys.AT,keys.AS)
        url = "https://api.twitter.com/1.1/search/tweets.json"
        keyword = "geocode:35.645736,139.747575,1.5km"
        params = {
            'q' : keyword,
            'count' :100,
            'max_id':max_id
        }
        response = twitter.get(url, params = params)
        return response


        # データベースに接続し保存
    def save_database(self,SQL):
        conn = mysql.connector.connect(
        user='root',
        password='',
        host='localhost',
        database='mirutsui')

        cur = conn.cursor()
        cur.execute(SQL)
        conn.commit()
        cur.close()
        conn.close()



    # httpレスポンスからSQL文を作成し返す
    def save_tweet(self,response,station='田町'):
        # HTTPレスポンスを引数にデータベースに保存する関数
        if response.status_code == 200:
            # 複数のツイートのデータが入ってる
            search_timeline = json.loads(response.text)

            # ツイートのデータを１つずつ取り出す
            for tweet in search_timeline['statuses']:
                data = {}
                data['tw_created_at'] = str(datetime.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))  
                data['tweet_id'] = tweet['id']
                # Python内でもエスケープシーケンスか効くので\\を二回使うで文字列を無効化
                data['text'] = tweet['text'].replace("\\","\\\\").replace("'","\\'")
                if(tweet['truncated'] == False):
                    data['truncated'] = 0
                else:
                    data['truncated'] = 1
                data['user_id'] = tweet['user']['id']
                data['user_name'] = tweet['user']['name'].replace("\\","\\\\").replace("'","\\'")
                data['screen_name'] = tweet['user']['screen_name']
                data['location'] = tweet['user']['location'].replace("\\","\\\\").replace("'","\\'")
                data['description'] = tweet['user']['description'].replace("\\","\\\\").replace("'","\\'")
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
                data['station'] = station
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
                print(SQL)
                self.save_database(SQL)


                if (self.max_id-1 > data['tweet_id']-1):
                    self.max_id = data['tweet_id']-1

            pprint(self.max_id)




        # エラーだった時の処理
        else:
            print("ERROR: %d" % response.status_code)
            if(response.status_code == 429):
                print("プログラムを一時停止します")
                time.sleep(4*60)





sample = Tweets_to_database()












