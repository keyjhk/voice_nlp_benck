from .views import *
from django.urls import path

appname='recorder'

urlpatterns=[
    path('',RecorderView.as_view())
]