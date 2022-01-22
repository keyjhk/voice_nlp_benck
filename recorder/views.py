import os, time
import redis

import django_redis
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings

from .models import *

# Create your views here.
TEMP_DIR = os.path.join(settings.MEDIA_ROOT, 'temp')
CACHE = django_redis.get_redis_connection()
QuesAnswers = QAPairs()


class RecorderView(APIView):
    def judge(self, func, *args, **kwargs):
        # api for judge function , return Boolean value
        # return func(*args,**kwargs)
        return True  # for test

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
        judge_result = self.judge(lambda q, a: True, file)
        file_url = request.build_absolute_uri(settings.MEDIA_URL + fname)
        return Response({'url': file_url, 'judge': judge_result}, status=status.HTTP_200_OK)

    def put(self, request):
        # merge part files
        fname = request.data['name']
        chunks = request.data['chunks']
        self.merge_files(fname, chunks)
        file_url = request.build_absolute_uri(settings.MEDIA_URL + fname)
        return Response({'url': file_url}, status=status.HTTP_200_OK)
