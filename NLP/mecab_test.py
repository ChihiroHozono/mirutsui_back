import MeCab

m = MeCab.Tagger ('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')

print(m.parse("ポケモンGOを東京駅でやってきた"))