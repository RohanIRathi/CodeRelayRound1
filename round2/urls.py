from django.conf.urls import url
from . import views

app_name = 'round2'

urlpatterns = [
    # /round2/question/(user_id)
    url(r'^question/(?P<user_id>[0-9]+)/$', views.question, name="question"),
    url(r'^add_que/(?P<user_id>[0-9]+)/$', views.add_que, name="add_que"),
    #/round2/login)
    url(r'^register/$', views.register, name="register"),
    #/round2/login/create_user
    url(r'^login/create_user1/$', views.create_user1, name="create_user1"),
    # /round2/user_id/(question_id)
    url(r'^(?P<user_id>[0-9]+)/(?P<question_id>[0-9]+)/$', views.question_details, name='question_details'),
    # /round2/question/(user_id)/(question_id)
    url(r'^(?P<user_id>[0-9]+)/(?P<question_id>[0-9]+)/next/$', views.handle_answer, name='handle_answer'),
    #url(r'^buy_question/(?P<user_id>[0-9]+)/(?P<question_id>[0-9]+)/$', views.buy_question, name='buy_question'),
    url(r'^leaderboard/(?P<user_id>[0-9]+)/$', views.leaderboard, name='leaderboard'),
    url(r'^instruction_view/(?P<user_id>[0-9]+)/(?P<question_id>[0-9]+)/$', views.instruction_view, name='instruction_view'),
    url(r'^(?P<user_id>[0-9]+)/(?P<question_id>[0-9]+)/$', views.save_answer, name='save_answer'),

]
