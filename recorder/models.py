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

    def get_qa(self, q):
        answer = self.get_answer(q)
        qpath = self.get_filepath(q)
        return {'question': q, 'answer': answer, 'path': qpath}

    def get_qalist(self):
        res = []
        q_list = self.redis.keys("question_*")
        for q in q_list:
            q = q.decode().split('question_')[-1]
            res.append(self.get_qa(q))
        return res

    def get_answer(self, question):
        answer = self.redis.get("question_" + question).decode()
        return answer

    def get_filepath(self, question):
        file_path = self.redis.get("path_" + question).decode()
        return file_path
