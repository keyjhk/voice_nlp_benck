import os, time
import redis

import django_redis
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
import sys
# sys.path.append('/home/wenet/runtime/server/x86/')
sys.path.insert(0,'/home/wenet/runtime/server/x86/')
#import voice2text

from .models import *

import gensim
import jieba
import re

model = gensim.models.KeyedVectors.load_word2vec_format('/home/model/word2vec_779845.bin',binary=True,unicode_errors='ignore')

# Create your views here.
TEMP_DIR = os.path.join(settings.MEDIA_ROOT, 'temp')
CACHE = django_redis.get_redis_connection()
QuesAnswers = QAPairs()


class RecorderView(APIView):

    def voice2t(self,voice_path):
        os.system('/home/wenet/runtime/server/x86/main.sh ' + voice_path)
        with open("/home/wenet/runtime/server/x86/log.txt", "r", encoding="utf-8") as fread:
            data = fread.read()
        print("**********************")
        data = "".join(data)
        text = re.findall(r'test Final result: (.*)', str(data))
        if (len(text) > 0):
            return text[0]
        else:
            return None

    def jieba_cut(self,content):
        word_list = []
        if content != "" and content is not None:
            seg_list = jieba.cut(content)
            for word in seg_list:
                # if word not in stop_word:
                word_list.append(word)
        return word_list

    # 清除不在词汇表中的词语
    def clear_word_from_vocab(self,word_list, vocab):
        new_word_list = []
        for word in word_list:
            if word in vocab:
                new_word_list.append(word)
        return new_word_list

    def text_sim(self,text1,text2):
        res1 = self.jieba_cut(text1)
        res2 = self.jieba_cut(text2)
        print(text1)
        print(text2)

        vocab = set(model.wv.vocab.keys())
        res1_clear = self.clear_word_from_vocab(res1, vocab)
        res2_clear = self.clear_word_from_vocab(res2, vocab)
        if len(res1_clear) > 0 and len(res2_clear) > 0:
            res = model.n_similarity(res1_clear, res2_clear)
            print(res)
            if float(res)>0.4:
                return True
            else:
                return False
        else:
            return None


    def judge(self,q,save_dir):
        # api for judge function , return Boolean value
        # return func(*args,**kwargs)
        #vt= voice2text(save_dir)
        text2=self.voice2t(save_dir)
        res=self.text_sim(q,text2)

        return res


        # return res  # for test

    def merge_files(self, fname, chunks):
        # pfname:fname_part_xx
        print('chunks', chunks)
        media_root = settings.MEDIA_ROOT
        temp_dir = TEMP_DIR
        part_files = filter(lambda pfname: fname in pfname, [file for file in os.listdir(temp_dir)])
        part_files = sorted(part_files, key=lambda x: int(x.split('part_')[-1]))[:chunks]
        # merge & remove
        with open(os.path.join(media_root, fname), 'wb') as f:
            for pf in part_files:
                temp_file = open(os.path.join(temp_dir, pf), 'rb')
                f.write(temp_file.read())
                temp_file.close()
                print('merge {}'.format(pf))
                os.remove(os.path.join(temp_dir, pf))

    def get(self, request):
        q,a = QuesAnswers.get_qa()
        # print(QuesAnswers.current_answer)
        return Response({'text': q})

    def post(self, request):
        file = request.data['file']  # audio file ,xx.wav
        # save
        save_dir = TEMP_DIR if request.data.get('is_chunk') else settings.MEDIA_ROOT
        if not os.path.exists(save_dir): os.mkdir(save_dir)
        fname = file.name
        save_dir = os.path.join(save_dir, fname)
        with open(save_dir, 'wb') as f:
            for chunk in file.chunks(): f.write(chunk)

        answer=QuesAnswers.current_answer  # string, the answer for current question
        print('answer for current question:',answer)
        judge_result = self.judge(answer,save_dir)
        file_url = request.build_absolute_uri(settings.MEDIA_URL + fname)
        return Response({'url': file_url, 'judge': judge_result}, status=status.HTTP_200_OK)

    def put(self, request):
        # merge part files
        fname = request.data['name']
        chunks = request.data['chunks']
        self.merge_files(fname, chunks)
        file_url = request.build_absolute_uri(settings.MEDIA_URL + fname)
        return Response({'url': file_url}, status=status.HTTP_200_OK)
