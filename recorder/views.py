import os, time

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings


# Create your views here.

class RecorderView(APIView):
    def merge_files(self, fname):
        # pfname:fname_part_xx
        print('fname:{}'.format(fname))
        media_root = settings.MEDIA_ROOT
        part_files = filter(lambda pfname: fname in pfname, [file for file in os.listdir(media_root)])
        part_files = sorted(part_files, key=lambda x: int(x.split('part_')[-1]))
        # merge & remove
        with open(os.path.join(media_root,fname), 'wb') as f:
            for pf in part_files:
                temp_file = open(os.path.join(media_root, pf), 'rb')
                f.write(temp_file.read())
                temp_file.close()
                print('merge {}'.format(pf))
                os.remove(os.path.join(settings.MEDIA_ROOT, pf))

    def get(self, request):
        return Response('hello recorder!')

    def post(self, request):
        file = request.data['file']
        # fname = str(int(time.time())) + '.wav'  # random file name
        fname = file.name
        with open(os.path.join(settings.MEDIA_ROOT, fname), 'wb') as f:
            for chunk in file.chunks(): f.write(chunk)

        file_url = request.build_absolute_uri(settings.MEDIA_URL + fname)
        return Response({'url': file_url}, status=status.HTTP_200_OK)

    def put(self, request):
        # merge part files
        file = request.data
        fname = file['name']
        self.merge_files(fname)
        file_url = request.build_absolute_uri(settings.MEDIA_URL + fname)
        return Response({'url': file_url}, status=status.HTTP_200_OK)