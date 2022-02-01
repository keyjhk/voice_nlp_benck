from .views import *
from django.urls import path

appname = 'recorder'

# use different http methods to follow rest design,not url name
# e.g. ,GET/POST /question/ ,not /getQuestion/

urlpatterns = [
    path('', RecorderView.as_view()),
    path('question/', QuestionView.as_view())
]
