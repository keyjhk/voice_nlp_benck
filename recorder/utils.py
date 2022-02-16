import gensim
import jieba
import os
import re

# # model = gensim.models.KeyedVectors.load_word2vec_format('E:\\PycharmProjects\\电信项目\\word2vec.bin',binary=True,unicode_errors='ignore')
# model = gensim.models.KeyedVectors.load_word2vec_format('/home/model/word2vec_779845.bin', binary=True,
#                                                         # unicode_errors='ignore')


def jieba_cut(content):
    word_list = []
    if content != "" and content is not None:
        seg_list = jieba.cut(content)
        for word in seg_list:
            # if word not in stop_word:
            word_list.append(word)
    return word_list


# 清除不在词汇表中的词语
def clear_word_from_vocab(word_list, vocab):
    new_word_list = []
    for word in word_list:
        if word in vocab:
            new_word_list.append(word)
    return new_word_list


# def text_sim(text1, text2):
#     res1 = jieba_cut(text1)
#     res2 = jieba_cut(text2)
#     print(text1)
#     print(text2)
#
#     vocab = set(model.wv.vocab.keys())
#     res1_clear = clear_word_from_vocab(res1, vocab)
#     res2_clear = clear_word_from_vocab(res2, vocab)
#     if len(res1_clear) > 0 and len(res2_clear) > 0:
#         res = model.n_similarity(res1_clear, res2_clear)
#         print(res)
#         if float(res) > 0.4:
#             return True
#         else:
#             return False
#     else:
#         return None

def text_sim_new(text1, text2):
    terms_reference = jieba.cut(text2)  # 默认精准模式
    terms_model = jieba.cut(text1)
    grams_reference = set(terms_reference)  # 去重；如果不需要就改为list
    grams_model = set(terms_model)
    temp = 0
    for i in grams_reference:
        if i in grams_model:
            temp = temp + 1
    fenmu = len(grams_model) + len(grams_reference) - temp  # 并集
    res = float(temp / fenmu)  # 交集

    if len(grams_model) > 0 and len(grams_reference) > 0:
        print(res)
        if float(res) > 0.3:
            return True
        else:
            return False
    else:
        return None

def text_sim_match(text1, text2):

    terms_reference = jieba.cut(text2)  # 默认精准模式
    terms_model = jieba.cut(text1)


    s1=set()
    for i in terms_model:
        s1.add(i)

    s2 = set()
    for i in terms_reference:
        s2.add(i)

    count=0
    for i in list(s2):
        if i in s1:
           count=count+1

    if count / len(s2)>0.7:
        return  True

    return False


def voice2t(voice_path):
    os.system(
        '/home/wenet/runtime/server/x86/main.sh ' + voice_path + ' 2>&1 | tee /home/wenet/runtime/server/x86/log.txt')
    with open("/home/wenet/runtime/server/x86/log.txt", "r", encoding="utf-8") as fread:
        data = fread.read()
    print("**********************")
    data = "".join(data)
    text = re.findall(r'test Final result: (.*)', str(data))
    
    if (len(text) > 0):
        print(text[-1])
        return text[-1]
    else:
        return None


def judge_deal(answer, save_dir):
    text2 = voice2t(save_dir)
    if text2!=None and text2!="":
        res = text_sim_match(text2,answer)
        return res
    return False
