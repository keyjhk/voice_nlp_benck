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
from .utils import *

import gensim
import jieba
import re

# model = gensim.models.KeyedVectors.load_word2vec_format('/home/model/word2vec_779845.bin',binary=True,unicode_errors='ignore')
# model = gensim.models.KeyedVectors.load_word2vec_format('E:\\PycharmProjects\\电信项目\\word2vec.bin',binary=True,unicode_errors='ignore')

# Create your views here.
TEMP_DIR = os.path.join(settings.MEDIA_ROOT, 'temp')
CACHE = django_redis.get_redis_connection()
QuesAnswers = QAPairs()


class RecorderView(APIView):

       # def voice2t(self,voice_path):
    #     os.system('/home/wenet/runtime/server/x86/main.sh ' + voice_path)
    #     with open("/home/wenet/runtime/server/x86/log.txt", "r", encoding="utf-8") as fread:
    #         data = fread.read()
    #     print("**********************")
    #     data = "".join(data)
    #     text = re.findall(r'test Final result: (.*)', str(data))
    #     if (len(text) > 0):
    #         return text[-1]
    #     else:
    #         return None


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
        judge_result = judge(answer,save_dir)
        file_url = request.build_absolute_uri(settings.MEDIA_URL + fname)
        return Response({'url': file_url, 'judge': judge_result}, status=status.HTTP_200_OK)

    def put(self, request):
        # merge part files
        fname = request.data['name']
        chunks = request.data['chunks']
        self.merge_files(fname, chunks)
        file_url = request.build_absolute_uri(settings.MEDIA_URL + fname)
        return Response({'url': file_url}, status=status.HTTP_200_OK)


class GetdataView(APIView):
    def get(self, request):
        # q, a = QuesAnswers.get_qa()
        # print(QuesAnswers.current_answer)
        q_list=QuesAnswers.get_qalist()
        return Response({'q_list': q_list},status=status.HTTP_200_OK)

class GetAnswerView(APIView):

    def post(self,request):
        file = request.data['file']  # audio file ,xx.wav
        question = request.data('question')

        save_dir = TEMP_DIR if request.data.get('is_chunk') else settings.MEDIA_ROOT
        if not os.path.exists(save_dir): os.mkdir(save_dir)
        fname = file.name
        save_dir = os.path.join(save_dir, fname)
        question = "question_" + question
        redis_answer=QuesAnswers.get_answer(question)
        res = judge(redis_answer,save_dir)

        return Response({'answer': res},status=status.HTTP_200_OK)

class GetFilepathView(APIView):
    def get(self,request):
        question = request.query_params.get('question')
        question="path_"+question
        file_path=QuesAnswers.get_filepath(question)
        return Response({'file_path': file_path},status=status.HTTP_200_OK)
