from .views import *
from django.urls import path,re_path

appname='recorder'

urlpatterns=[
    path('',RecorderView.as_view()),
    re_path(r'^getQlist/$',GetdataView.as_view()),
    re_path(r'^getAnswer/$',GetAnswerView.as_view()),
]