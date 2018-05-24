from gensim.models import word2vec
# 新たなデータ型？ぽい
from collections import defaultdict
from sklearn.cluster import KMeans


# W2Vのモデル
model = word2vec.Word2Vec.load("/Users/chihiro/Python/mirutsui_back/NLP/ver19_comment.model")
vocab = list(model.wv.vocab.keys())
vectors = [model.wv[word] for word in vocab]
#verboseは詳細な分析結果を表示、
kmeans_model = KMeans(n_clusters=150, random_state=0,verbose=1,n_init=10,n_jobs=-1)
kmeans_model.fit(vectors)
cluster_labels = kmeans_model.labels_
cluster_to_words = defaultdict(list)
for cluster_id, word in zip(cluster_labels, vocab):
    cluster_to_words[cluster_id].append(word)

for words in cluster_to_words.values():
    print(words)
    print()



