import gensim
import jieba
model = gensim.models.KeyedVectors.load_word2vec_format('E:\\PycharmProjects\\电信项目\\word2vec.bin',binary=True,unicode_errors='ignore')

def jieba_cut(self, content):
    word_list = []
    if content != "" and content is not None:
        seg_list = jieba.cut(content)
        for word in seg_list:
            # if word not in stop_word:
            word_list.append(word)
    return word_list


# 清除不在词汇表中的词语
def clear_word_from_vocab(self, word_list, vocab):
    new_word_list = []
    for word in word_list:
        if word in vocab:
            new_word_list.append(word)
    return new_word_list

def text_sim(text1, text2):
    res1 = jieba_cut(text1)
    res2 = jieba_cut(text2)
    print(text1)
    print(text2)

    vocab = set(model.wv.vocab.keys())
    res1_clear = clear_word_from_vocab(res1, vocab)
    res2_clear = clear_word_from_vocab(res2, vocab)
    if len(res1_clear) > 0 and len(res2_clear) > 0:
        res = model.n_similarity(res1_clear, res2_clear)
        print(res)
        if float(res) > 0.4:
            return True
        else:
            return False
    else:
        return None

def judge(answer_redis,save_dir):
    # api for judge function , return Boolean value
    # return func(*args,**kwargs)
    #vt= voice2text(save_dir)
    # text2=self.voice2t(save_dir)
    text2 ="你好"
    res=text_sim(answer_redis,text2)
    return res