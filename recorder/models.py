import django_redis
from django.db import models


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
