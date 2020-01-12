from django.db import models


class User(models.Model):
    login_name = models.CharField(max_length=100)
    phone_number1 = models.IntegerField(default=0)
    phone_number2 = models.IntegerField(default=0)
    college_name1 = models.CharField(max_length=100)
    college_name2 = models.CharField(max_length=100, default = '')
    user_name1 = models.CharField(max_length=100)
    user_name2 = models.CharField(max_length=100, default = '')
    email1 = models.CharField(max_length=100)
    email2 = models.CharField(max_length=100, default = '')
    total_score = models.IntegerField(default=0)
    end_time = models.IntegerField(default=0)
    #score = models.TextField()
    money = models.IntegerField(default=0)
    easy_counter = models.IntegerField(default=0)
    cnt = models.IntegerField(default = 1)

    def __str__(self):
        return str(self.pk)


class Question(models.Model):
    question = models.TextField(max_length=4000)
    question_title = models.CharField(max_length=2000)
    input = models.CharField(default=0, max_length=15000)
    correct_op = models.CharField(default=0, max_length=10000)
    explanation = models.TextField(max_length=7000)
    test_input = models.TextField(max_length=100000)

    test_output = models.TextField(max_length=10000)
    cost = models.IntegerField(default = 100)
    user = models.ManyToManyField(User, null=True, through="Score")
    type = models.CharField(default="Easy", max_length=10)

    def __str__(self):
        return self.question_title


class Score(models.Model):
    user_f = models.ForeignKey(User, on_delete=models.CASCADE)
    question_f = models.ForeignKey(Question, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    language_preferred = models.CharField(default='c', max_length=500)

