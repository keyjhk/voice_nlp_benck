import django_redis
from django.db import models
from django.core.cache import cache
from django.db import connection


# Create your models here.
class QAPairs:
    def __init__(self):
        # self.redis = django_redis.get_redis_connection()
        # self.pairs = iter(self.qa())
        self.current_question = ''
        self.current_answer = ''

    # def qa(self):
    #     while True:
    #         for question in self.redis.keys():
    #             answer = self.redis.get(question)
    #             try:
    #                 yield question.decode(), answer.decode()  # binary b'xx'
    #             except Exception:
    #                 continue

    def get_qa(self, q):
        # answer = self.get_answer(q)
        # qpath = self.get_filepath(q)
        with connection.cursor() as cursor:
            # 执行sql语句
            cursor.execute("select answer,q_path,a_path from quary_table WHERE  question= %s", q)
            # 查出一条数据
            row = cursor.fetchone()
            if row !=None:
                return {'question': q, 'answer': row[0], 'q_path': row[1],'a_path': row[2]}

    def get_qalist(self):
        res = []
        # q_list = self.redis.keys("question_*")
        # for q in q_list:
        #     q = q.decode().split('question_')[-1]
        #     res.append(self.get_qa(q))
        with connection.cursor() as cursor:
            # 执行sql语句
            cursor.execute("select question,answer,q_path,a_path from quary_table WHERE  group_class=1")
            # 查出一条数据
            rows = cursor.fetchall()
            if rows !=None:
                for i in rows:
                    res.append({'question': i[0], 'answer': i[1], 'q_path': i[2],'a_path': i[3]})
        return res
        # return res

    # def get_answer(self, question):
    #     answer = self.redis.get("question_" + question).decode()
    #     return answer
    #
    # def get_filepath(self, question):
    #     file_path = self.redis.get("path_" + question).decode()
    #     return file_path
