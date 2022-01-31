import django_redis
from django.db import models
from django.core.cache import cache


# Create your models here.
class QAPairs:
    def __init__(self):
        self.redis = django_redis.get_redis_connection()
        self.pairs = iter(self.qa())
        self.current_question = ''
        self.current_answer = ''

    def qa(self):
        while True:
            for question in self.redis.keys():
                answer = self.redis.get(question)
                try:
                    yield question.decode(), answer.decode()  # binary b'xx'
                except Exception:
                    continue

    def get_qa(self):
        self.current_question, self.current_answer = next(self.pairs)
        return self.current_question,self.current_answer

    def get_qalist(self):
        q_list= self.redis.keys("question_*")

        return q_list


    def get_answer(self,question):
        answer = self.redis.get(question)
        return answer

    def get_filepath(self,question):
        file_path = self.redis.get(question)
        return file_path