#グルナビの口コミを分かちかきしてリスト形式で別ファイルに保存

import mysql.connector
# 形態素解析器
from janome.tokenizer import Tokenizer
t = Tokenizer()

import pickle
from gensim.models import word2vec
import logging
from pprint import pprint

def make_comment_list():

	# データベースから取得する処理
	conn = mysql.connector.connect(
		    user='root',
	        password='',
	        host='localhost',
	        database='mirutsui')
	cur = conn.cursor()


	# 取得するデータの総数
	SQL = "SELECT COUNT(*) FROM `tabelog_comments`";
	cur.execute(SQL)
	total = cur.fetchall()[0][0]

	print('取得するデータの総数は' + str(total) + '件です')

	# 食べログのコメントの取得
	SQL = "SELECT `comment` FROM `tabelog_comments`"
	cur.execute(SQL)

	# 分かち書きした単語保存するリスト
	docs = []

	# 分かち書きした文章の数
	count = 0
	# 分かち書きし、その単語をリストに保存する
	for comment in cur.fetchall():
		# 口コミのデータ
		tokens = t.tokenize(comment[0])
		for token in tokens:
			# 品詞の切り分け
			part_of_speech = token.part_of_speech.split(",")[0]
			if (part_of_speech == '名詞') or (part_of_speech == '形容詞') or (part_of_speech == '動詞'):
				# 読みが一文字の単語、数、代名詞は追加しない
				if(len(token.reading) > 1) and (token.part_of_speech.split(',')[1] != '数') and(token.part_of_speech.split(',')[1] != '代名詞'):
					docs.append(token.base_form)


		# 口コミと全体の進度の表示
		count +=1
		print('全体の'+ str(count/total * 100) +'%が完了しました')
	print(docs)
	# 変数をバイナリデータで保存
	with open('/Users/chihiro/Python/mirutsui_back/NLP/docs.binaryfile','wb')as f:
		pickle.dump(docs,f)


	cur.close()
	conn.close()

# 分かち書きされたリストを返す
def return_list():
	# バイナリデータを開く
	with open('/Users/chihiro/Python/mirutsui_back/NLP/docs.binaryfile','rb')as f:
		docs = pickle.load(f)

	return docs

# modelを作る
def make_doc2vec():
	sentences = return_list()
	model = word2vec.Word2Vec(sentences, size=200, min_count=10, window=15,iter=20)
	model.save("/Users/chihiro/Python/mirutsui_back/NLP/comment.model")

# モデルの読み込み
def similar_word(word):
	model = word2vec.Word2Vec.load("/Users/chihiro/Python/mirutsui_back/NLP/comment.model")
	result = model.most_similar(positive=[word])
	pprint(result)



similar_word('美味しい')






