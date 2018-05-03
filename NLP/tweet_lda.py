import MeCab
mecab = MeCab.Tagger ('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
import mysql.connector
import pickle
import gensim
from gensim import corpora,models,similarities
from pprint import pprint
# 正規化を行う
import neologdn

def make_corplist():

    # データベースから取得する処理
    conn = mysql.connector.connect(
            user='root',
            password='',
            host='localhost',
            database='mirutsui')
    cur = conn.cursor()


    # 取得するデータの総数
    SQL = "SELECT COUNT(*) FROM `tweet_data`"
    cur.execute(SQL)
    total = cur.fetchall()[0][0]
    print('取得するデータの総数は' + str(total) + '件です')

    # ツイートの取得
    # 改行を消す
    SQL = "SELECT `text` FROM `tweet_data`;"
    cur.execute(SQL)

    corplist = []
    # 分かち書きし、corplistに保存
    for tweet in cur.fetchall():
        # ツイートを渡す前に正規化
        tweet = normalization(tweet[0])
        corplist.append(parser(tweet))
        print(corplist)

    cur.close()
    conn.close()

    print(corplist)

# 正規化を行う関数
# 全角を半角にしたり、大文字を小文字にしたり、ルールベースで文字を変換すること
def normalization(text):
    text = neologdn.normalize(text)
    # 大文字を小文字に変換
    text = text.lower()
    return text



def parser(text):
    # 表層形を入れるリスト
    corplist = []
    # ノードとは単語と品詞を意味する
    mecab.parse("")
    node = mecab.parseToNode(text)
    while node:
        if(len(node.surface) == 0):
            # node.nextで次のnodeへ移動が出来る
            node = node.next
            continue
            # featureには品詞や基本形などの特徴が入っている
        if(node.feature.split(",")[0] == u'名詞'):
            corplist.append(node.surface)
        node = node.next
    return corplist



# データに直接parserをかける
def analyzer(content):
    # トークンには文章毎の表層形が入ってる
    token = []
    for i in content:
        token_p = parser(i)
        token_append(token_p)
    return token


def make_model(words):

    # 辞書の作成
    # 頻出単語群の作成
    dictionary = corpora.Dictionary(words)
    # dictionary.filter_extremesで辞書に単語を加える時の条件を付加
    # no_below=2      文章郡全体で二回以上出現した単語
    # no_above=0.01   全体の1%以下の出現率である単語
    dictonary.filter_extremes(no_below=2,no_above=0.01)

    # コーパスの作成
    # 辞書中の各単語にそれらがどれだけの頻度で出現したかを紐づけるリスト
    corpus = [dictonary.doc2bow(text) for text in words]

    # トピックモデルを作成
    lda = gensim.models.ldamodel.LdaModel(corpus=corpus,num_topics=10)

    # 各トピックの出現頻出度の上位を表示
    topic_top = []
    for topic in lda.show_topics(-1,formatted=False):
        topic_top.append([dictionary[int(tag[0])] for tag in topic[1]])

    print(topic_top)


# おそらくmake_modelの引数には文章毎の分かち書きされた単語のリストを入れる必要がある
make_corplist()









