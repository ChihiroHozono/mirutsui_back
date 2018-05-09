#グルナビの口コミを分かちかきしてリスト形式で別ファイルに保存

import mysql.connector
# 形態素解析器
from janome.tokenizer import Tokenizer
t = Tokenizer()
import pickle
from gensim.models import word2vec
from pprint import pprint
import neologdn


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
		# 口コミのデータを正規化
		comment = neologdn.normalize(comment[0])
		tokens = t.tokenize(comment)
		# リストのリスト
		doc =[]
		for token in tokens:

			# 品詞の切り分け
			part_of_speech = token.part_of_speech.split(",")[0]
			# 品詞の詳細
			kind_part_of_speech = token.part_of_speech.split(",")[1]
			# 名詞、動詞、形容詞、形容動詞のみをフィルタリング
			if (part_of_speech == '名詞') or (part_of_speech == '動詞') or (part_of_speech == "形容動詞") or (part_of_speech == '形容詞'):
				# 下記の条件の時はデータセットに追加しない
				if(kind_part_of_speech != '数') and (kind_part_of_speech != 'サ変接続') and (token.surface != '円') and (len(token.reading) >= 2):
					# print(token)
					doc.append(token.base_form)
		docs.append(doc)



		# 口コミと全体の進度の表示
		count +=1
		print('全体の'+ str(count/total * 100) +'%が完了しました')
	print(docs)

	# 変数をバイナリデータで保存
	with open('/Users/chihiro/Python/mirutsui_back/NLP/ver15_docs.binaryfile','wb')as f:
		pickle.dump(docs,f)

	cur.close()
	conn.close()

# 分かち書きされたリストを返す
def return_list():
	# バイナリデータを開く
	with open('/Users/chihiro/Python/mirutsui_back/NLP/ver15_docs.binaryfile','rb')as f:
		docs = pickle.load(f)

	return docs

# modelを作る
def make_doc2vec():
	sentences = return_list()
	model = word2vec.Word2Vec(sentences, size=400, min_count=80, window=10,iter=5)
	model.save("/Users/chihiro/Python/mirutsui_back/NLP/ver19_comment.model")


# 類義語判定
def similar_word(word):
	model = word2vec.Word2Vec.load("/Users/chihiro/Python/mirutsui_back/NLP/ver19_comment.model")
	result = model.most_similar(positive=[word])
	print(word + 'に類似した単語')
	pprint(result)


word_list=['魚','マグロ','うに','美味い','ラーメン','鉛筆','雨','1','金','りんご']

# リスト形式で格納されている各単語の類似度を表示
def return_similar_word(word_list):
	for word in word_list:
		# Var12はデータセットをbaseformにしたので単語の類似度もbaseform
		word = t.tokenize(word)
		for word in word:
			word = word.base_form
			try:
				similar_word(word)
			except Exception:
				print(word + 'はデータにありません')
				print(Exception.args)
				pass



# print(return_list())
# make_comment_list()
make_doc2vec()
# similar_word('カレー')
# return_similar_word(word_list)











