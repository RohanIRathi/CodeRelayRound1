import os
import signal

from django.shortcuts import render, HttpResponse
from .models import User, Question, Score
import subprocess
from subprocess import Popen, PIPE, STDOUT
import json
import random, math
# import pyperclip
# from subprocess import Popen, PIPE
import time
import threading

import signal, sys

time_finish = True
ps_id = 0
tle = False
question_list = []


# Working code
tle_array = [False for i in range(20)]


def check_tle(pid, i):
    time.sleep(1)
    #     global tle
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
        tle_array[i] = True
    except:
        tle_array[i] = False

# Ends here

def timeout(sig, frm):
    print('timeout')
    # time_finish = True
    if time_finish == True:
        print("Finished")
        os.killpg(os.getpgid(ps_id), signal.SIGTERM)
        tle = True
        return HttpResponse("TLE")
        # raise Exception

    signal.signal(signal.SIGALRM, timeout)


def question(request, user_id):
    all_questions = Question.objects.all()
    current_user = User.objects.get(pk=user_id)
    jsonDec = json.decoder.JSONDecoder()
    # all_marks = list(jsonDec.decode(current_user. score))
    current_user.total_score = 0
    temp = 0
    # for marks in all_marks:
    #     temp += marks
    question_list = []
    for questions in all_questions:
        if current_user in questions.user.all():
            question_list.append({"question": questions,
                                  "status": "bought",
                                  "cost": questions.cost,
                                  "difficulty": questions.type,
                                  "question_score": Score.objects.get(user_f=current_user, question_f=questions).score})

    current_user.total_score = temp
    if current_user.cnt <= 2:
    	current_user.end_time=(time.time() + (60 * 15))
    elif current_user.cnt > 2 and current_user.cnt <= 3:
    	current_user.end_time = (time.time() + (60 * 10))
    current_user.save()
    print(current_user.total_score)
    # return render(request, 'round2/questions_list.html', {'all_questions' : all_questions, 'user_id': user_id,'remaining_time':current_user.end_time-time.time(),'all_marks':all_marks ,'one':50,'two':50,'three':100,'four':100})
    return render(request, 'round2/select_questions_new.html',
                  {'buyed_questions': '', 'all_questions': all_questions, 'user_id': user_id,
                   'remaining_time': current_user.end_time - time.time(), 'question_list': question_list,
                   'money': current_user.money})


def register(request):
    return render(request, 'round2/register_new.html', {})


def create_user1(request):
    team_name = request.POST.get('team_name')
    participant1 = request.POST.get('participant1')
    participant2 = request.POST.get('participant2')
    mobile1 = request.POST.get('mobile1')
    college1 = request.POST.get('college1')
    email1 = request.POST.get('email1')
    reciept_number = request.POST.get('reciept_number')
    msg = ''
    
    question_list = Question.objects.all()
    new_user = User(login_name=team_name, phone_number1=mobile1,
                    college_name1=college1, user_name1=participant1, user_name2=participant2, email1=email1,
                    end_time=(time.time() + (60 * 10)), cnt = 1)
    new_user.cnt = 1
    print(new_user.end_time)
    new_user.save()
                    
    random_index = math.floor(random.random()*len(question_list))
    question = question_list[random_index]
    score_ob = Score(user_f = new_user , question_f = question)
    score_ob.save()
    # return question(request,new_user.pk)
    return instruction_view(request, new_user.pk, question.pk)
    

def question_details(request, user_id, question_id):
    selected_question = Question.objects.get(pk=question_id)
    # print(selected_question)
    current_user = User.objects.get(pk=user_id)
    if current_user.cnt <= 3:
        current_user.end_time = (time.time() + (60 * 15))
    elif current_user.cnt > 3 and current_user.cnt <= 6:
        current_user.end_time = (time.time() + (60 * 10))
    current_user.save()
    try:
        score_object = Score.objects.get(user_f=current_user, question_f=selected_question)
        language = score_object.language_preferred
    except:
        language = 'c'

    file_extension = 'c'

    if language == 'cpp':
        file_extension = 'cpp'
    elif language == 'cpp14':
        file_extension = 'cpp'

    # print(current_user.end_time)
    # print(current_user.end_time - time.time())

    input_file = str(question_id) + '_' + str(user_id)
    bought = False
    if current_user in selected_question.user.all():
        bought = True

    jsonDec = json.decoder.JSONDecoder()
    # current_user.total_score = 0
    # all_marks = list(jsonDec.decode(current_user.score))
    # for marks in all_marks:
    #     current_user.total_score += marks
    current_user.save()
    if os.path.isfile(input_file + '.' + file_extension):
        f = open(input_file + '.' + file_extension, 'r')
        f.flush()
        previous_code = f.read()
        f.close()
    else:
        previous_code = ""

    return render(request, 'round2/question_details.html',
                  {'pegs_id': int("3"), 'bought': bought, 'selected_question': selected_question,
                   'question_id': selected_question.pk,
                   'user_id': user_id, 'submitted_code': previous_code,
                   'remaining_time': current_user.end_time - time.time(),
                   'money':0, 'language': language})


def handle_answer(request, user_id, question_id):
    if request.POST.get("finish"):
        return leaderboard(request, user_id)
    # code = request.POST.get("text_area")
    # print(language)
    input_file = str(question_id) + '_' + str(user_id)
    language = request.POST.get("language")

    file_extension = 'c'
    # changes more
    compiler = 'gcc '
    #print('This is the language selected ' + language)
    if language == 'cpp':
        compiler = 'g++ -std=c++11 '
        file_extension = 'cpp'

    elif language == 'cpp14':
        compiler = 'g++ -std=c++14 '
        file_extension = 'cpp'

    code = request.POST.get("text_area")
    f = open(input_file + '.' + file_extension, 'w')
    # f=open('test.cpp','w')
    f.write(code)
    f.close()

    current_user = User.objects.get(pk=user_id)
    current_question = Question.objects.get(pk=question_id)
    score_object = Score.objects.get(user_f=current_user, question_f=current_question)
    jsonDec = json.decoder.JSONDecoder()

    score_object.language_preferred = language
    score_object.save()


    compile_output = subprocess.getoutput(
        compiler + ' -o ' + input_file + ' ' + input_file + '.' + file_extension)

    if not compile_output:
        correct_op = jsonDec.decode(current_question.correct_op)

        input_value = jsonDec.decode(current_question.input)
        print('this is input values list')
        print(input_value)

        checker = [None] * len(correct_op)

        score = 0
        score_for_one = (current_question.cost) / len(correct_op)

        for tc in range(0, len(input_value)):
            print(tc)
            input_str = ""
            for i in input_value[tc]:
                input_str += (str(i) + '\n')

            print('giving this as input ' + input_str)

            process = Popen(['./' + input_file], shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE, preexec_fn=os.setsid)
            tle_array[tc] = False

            process.stdin.write(input_str.encode())
            process.stdin.flush()

            tle_thread = threading.Thread(target=check_tle, args=(process.pid, tc))
            tle_thread.start()

            errors = ""
            # errors = process.stderr.readline()

            output = process.communicate()[0].rstrip()

            if tle_array[tc]:
                print('Time Limit Exceed')
                checker[tc] = 2
            else:

                try:
                    output = output.decode()
                except:
                    pass

                print('This is the output of program')
                print(output)
                # generated_output = output.split()
                # print(generated_output)
                # score = 0
                # score_for_one = (current_question.cost * 2) / len(correct_op)
                print('This is the correct output')
                print(correct_op[tc])

                if(current_question.pk == 15):
                    output = float(output)
                    check = float(correct_op[tc])

                    if(check-output < 0.000001 or output-check < 0.000001):
                        score += score_for_one
                        checker[tc] = 1

                if (current_question.pk != 15 and str(output) == str(correct_op[tc])):
                    print("And this is correct")
                    score += score_for_one
                    checker[tc] = 1

            tle_array[tc] = False
        if score >= 75:
        	score += (current_user.end_time - time.time()) * 0.1
        if score > score_object.score:
            current_user.total_score += (score - score_object.score)
            current_user.save()
            score_object.score = score
            score_object.save()

        return render(request, 'round2/question_details.html',
                      {'pegs_id': int("3"), 'error_msg': False, 'submitted': True, 'one': 50, 'two': 50,
                       'three': 100, 'four': 100, 'submitted_code': code, 'selected_question': current_question,
                       'user_id': user_id, 'checker': checker, "one_score":score_for_one,
                       'remaining_time': current_user.end_time - time.time(), 'error_msg': errors,
                       'bought': True, 'question_id': question_id, 'question_score': score_object.score,
                       'money': current_user.money, 'language': score_object.language_preferred})


    else:
        print('something else')
        output_to_display = compile_output
        return render(request, 'round2/question_details.html',
                      {'pegs_id': int("3"), 'submitted': False, 'submitted_code': code,
                       'selected_question': current_question,
                       'user_id': user_id, 'checker': False,
                       'remaining_time': current_user.end_time - time.time(), 'error_msg': str(output_to_display)
                          , "question_id": question_id, 'bought': True, 'money': current_user.money,
                       'language': score_object.language_preferred})


############################################33

    #
    # correct_op = jsonDec.decode(current_question.correct_op)
    #
    # checker = [None] * len(correct_op)
    # input_value = jsonDec.decode(current_question.input)
    #
    # score = 0
    # score_for_one = (current_question.cost * 2) / len(correct_op)
    #
    # print('this is input values list')
    # print(input_value)
    #
    # for tc in range(0,len(input_value)):
    #     input_str = ""
    #     for i in input_value[tc]:
    #         input_str += (str(i) + '\n')
    #
    #     print('giving this as input ' + input_str)
    #
    #     compile_output = subprocess.getoutput(
    #         compiler + ' -o ' + input_file + ' ' + input_file + '.' + file_extension)
    #
    #     if not compile_output:
    #         process = Popen(['./' + input_file], shell=True, stdout=PIPE, stdin=PIPE, preexec_fn=os.setsid)
    #         tle_array[tc] = False
    #
    #         process.stdin.write(input_str.encode())
    #         process.stdin.flush()
    #
    #         tle_thread = threading.Thread(target=check_tle, args=(process.pid, tc))
    #         tle_thread.start()
    #
    #         output = process.stdout.readline()
    #
    #         if tle_array[tc]:
    #             print('Time Limit Exceed')
    #         else:
    #             output = output.decode()
    #             print(output)
    #             # generated_output = output.split()
    #             # print(generated_output)
    #             score = 0
    #             score_for_one = (current_question.cost * 2) / len(correct_op)
    #             if output == correct_op[tc]:
    #                 score += score_for_one
    #
    #             if score > score_object.score:
    #                 current_user.money += (score - score_object.score)
    #                 current_user.save()
    #                 score_object.score = score
    #                 score_object.save()
    #
    #             return render(request, 'round2/question_details.html',
    #                           {'pegs_id': int("3"), 'error_msg': False, 'submitted': True, 'one': 50, 'two': 50,
    #                            'three': 100, 'four': 100, 'submitted_code': code, 'selected_question': current_question,
    #                            'user_id': user_id, 'checker': checker,
    #                            'remaining_time': current_user.end_time - time.time(), 'error_msg': "",
    #                            'bought': True, 'question_id': question_id, 'question_score': score_object.score,
    #                            'money': current_user.money, 'language': score_object.language_preferred})
    #
    #         tle_array[tc] = False
    #
    #     else:
    #         print('something else')
    #         output_to_display = compile_output
    #         return render(request, 'round2/question_details.html',
    #                       {'pegs_id': int("3"), 'submitted': False, 'submitted_code': code,
    #                        'selected_question': current_question,
    #                        'user_id': user_id, 'checker': False,
    #                        'remaining_time': current_user.end_time - time.time(), 'error_msg': str(output_to_display)
    #                           , "question_id": question_id, 'bought': True, 'money': current_user.money,
    #                        'language': score_object.language_preferred})
    #



        # print('input: '+input_str)
        # compile_output = subprocess.getoutput(
        #     compiler + ' -o ' + input_file + ' ' + input_file + '.' + file_extension)
        #
        # if not compile_output:
        #     # compile_output = subprocess.getoutput('a.exe < input_file.txt')
        #     compile_output = subprocess.getoutput(
        #         './' + input_file + ' <' + input_file + '.txt')  # TLE Logic to e implemented here
        #     output_to_display = False
        #     print('compile ' + compile_output)
        #     generated_output = compile_output.split()
        #     # generated_output = compile_output
        #     # print(generated_output + "sd")
        #
        #     print(len(generated_output) + len(correct_op))
        #     if len(generated_output) < len(correct_op):
        #         output_to_display = compile_output
        #         iterable_length = len(generated_output)
        #     elif len(generated_output) > len(correct_op):
        #         output_to_display = compile_output
        #         iterable_length = len(correct_op)
        #     else:
        #         iterable_length = len(correct_op)
        #
        #     score = 0
        #     score_for_one = (current_question.cost * 2) / len(correct_op)
        #
        #     for i in range(iterable_length):
        #         if generated_output[i] == str(correct_op[i]):
        #             checker[i] = True
        #             score += score_for_one
        #
        #     # print(score, score_object.score)
        #     if score > score_object.score:
        #         current_user.money += (score - score_object.score)
        #         current_user.save()
        #         score_object.score = score
        #         score_object.save()
        #
        #     return render(request, 'round2/question_details.html',
        #                   {'pegs_id': int("3"), 'error_msg': False, 'submitted': True, 'one': 50, 'two': 50,
        #                    'three': 100, 'four': 100, 'submitted_code': code, 'selected_question': current_question,
        #                    'user_id': user_id, 'checker': checker,
        #                    'remaining_time': current_user.end_time - time.time(), 'error_msg': output_to_display,
        #                    'bought': True, 'question_id': question_id, 'question_score': score_object.score,
        #                    'money': current_user.money, 'language': score_object.language_preferred})
        #
        # else:
        #     print('something else')
        #     output_to_display = compile_output
        #     return render(request, 'round2/question_details.html',
        #                   {'pegs_id': int("3"), 'submitted': False, 'submitted_code': code,
        #                    'selected_question': current_question,
        #                    'user_id': user_id, 'checker': False,
        #                    'remaining_time': current_user.end_time - time.time(), 'error_msg': str(output_to_display)
        #                       , "question_id": question_id, 'bought': True, 'money': current_user.money,
        #                    'language': score_object.language_preferred})

    # input_str = ""
    # for i in input_value:
    #     input_str += (str(i) + ' ')
    # print('this is input'+input_str)
    #
    # f = open(input_file + '.txt', 'w')
    # f.write(input_str)
    # f.close()
    #
    # compile_output = subprocess.getoutput(
    #     compiler + ' -o ' + input_file + ' ' + input_file + '.' + file_extension)
    #
    # if not compile_output:
    #     # compile_output = subprocess.getoutput('a.exe < input_file.txt')
    #     compile_output = subprocess.getoutput(
    #         './' + input_file + ' <' + input_file + '.txt')  # TLE Logic to e implemented here
    #     output_to_display = False
    #
    #     generated_output = compile_output.split()
    #
    #     # print(type(generated_output),type(correct_op))
    #
    #     if len(generated_output) < len(correct_op):
    #         output_to_display = compile_output
    #         iterable_length = len(generated_output)
    #     elif len(generated_output) > len(correct_op):
    #         output_to_display = compile_output
    #         iterable_length = len(correct_op)
    #     else:
    #         iterable_length = len(correct_op)
    #
    #     score = 0
    #     score_for_one = (current_question.cost*2)/len(correct_op)
    #
    #     for i in range(iterable_length):
    #         if generated_output[i] == str(correct_op[i]):
    #             checker[i] = True
    #             score += score_for_one
    #
    #     print(score,score_object.score)
    #     if score > score_object.score:
    #         current_user.money += (score - score_object.score)
    #         current_user.save()
    #         score_object.score = score
    #         score_object.save()
    #
    #     return render(request, 'round2/question_details.html',
    #               {'pegs_id': int("3"), 'error_msg': False, 'submitted': True, 'one': 50, 'two': 50,
    #                'three': 100, 'four': 100, 'submitted_code': code, 'selected_question': current_question,
    #                'user_id': user_id, 'checker': checker,
    #                'remaining_time': current_user.end_time - time.time(), 'error_msg': output_to_display,
    #                'bought': True, 'question_id': question_id, 'question_score': score_object.score,
    #                'money': current_user.money, 'language': score_object.language_preferred})
    #
    # else:
    #     print('something else')
    #     output_to_display = compile_output
    #     return render(request, 'round2/question_details.html',
    #                   {'pegs_id': int("3"), 'submitted': False, 'submitted_code': code,
    #                    'selected_question': current_question,
    #                    'user_id': user_id, 'checker': False,
    #                    'remaining_time': current_user.end_time - time.time(), 'error_msg': str(output_to_display)
    #                       , "question_id": question_id, 'bought': True, 'money': current_user.money, 'language': score_object.language_preferred})

    # output after running the code with test cases




    output_to_display = ""

    # compile_output = subprocess.getoutput(
    #     compiler str(question_id)+'_'+str(user_id)+'.'+str(language) && ./a.out < input.txt)
    # print('>>'+compile_output+'<<')
    # output_to_display = compile_output

    # print(correct_op)

    #sucessfully compiled
    # if not compile_output:
    #     print(correct_op + 'complie_op'  + compile_output)
    #     return render(request, 'round2/question_details.html',
    #                           {'pegs_id': int("3"), 'error_msg': False, 'submitted': True, 'one': 50, 'two': 50,
    #                            'three': 100, 'four': 100, 'submitted_code': code, 'selected_question': current_question,
    #                            'user_id': user_id, 'checker': False,
    #                            'remaining_time': current_user.end_time - time.time(),
    #                            'bought': True, 'question_id': question_id, 'question_score': score_object.score,
    #                            'money': current_user.money})



    # if request.POST.get("submit"):
    #     '''pyperclip.copy('The text to be copied to the clipboard.')
    #         return render(request, 'round2/question_details.html',
    #                   {'submitted': True, 'submitted_code': str(code), 'selected_question': current_question,
    #                    'user_id': user_id})'''
    #
    #     t = 0
    #     # from subprocess import CalledProcessError, check_output
    #     # compile_ouput = subprocess.getoutput(
    #     #     'g++ ' + str(question_id) + '_' + str(user_id) + '.cpp -o ' + str(question_id) + '_' + str(
    #     #         user_id) + '.out')
    #     marks = 0
    #     current_user = User.objects.get(pk=user_id)
    #     # Successfully complied
    #     if not compile_output:
    #         print('compiled')
    #         '''f = open('output.txt', 'w')
    #                     output = subprocess.check_output('a.exe', universal_newlines=True, shell=True)
    #                     f.write(output)
    #                     f.close()'''
    #
    #         input_length = len(input)
    #         counter = 0
    #         result = [None] * len(input)
    #         checker = [None] * len(input)
    #         try:
    #             for ii in input:
    #
    #                 p = Popen(['./' + str(question_id) + '_' + str(user_id) + '.out'], shell=True, stdout=PIPE,
    #                           stdin=PIPE,
    #                           preexec_fn=os.setsid)
    #                 value = str(ii) + '\n'
    #                 value = bytes(value, 'UTF-8')  # Needed in Python 3.
    #
    #                 p.stdin.write(value)
    #                 p.stdin.flush()
    #                 global time_finish
    #                 time_finish = True
    #                 global ps_id
    #                 ps_id = p.pid
    #                 # print(ps_id)
    #                 # signal.alarm(5)
    #                 global tle
    #                 tle = False
    #                 result[counter] = str(p.stdout.readline().rstrip())
    #                 time_finish = False
    #                 print("answr : ", correct_op[counter], result[counter])
    #                 a = result[counter] + "b''"
    #                 temp = ""
    #                 result[counter] = result[counter][2:len(result[counter]) - 1]
    #
    #                 # print(a)
    #                 # print(result[counter])
    #                 while not temp == "b''" and str(result[counter]).__len__() <= str(correct_op[counter]).__len__():
    #                     # result += "<br>"
    #                     temp = str(p.stdout.readline().rstrip())
    #                     if not temp == "b''":
    #                         temp = temp[2:len(temp) - 1]
    #                         result[counter] += temp
    #                     # print(result)
    #
    #                 if str(correct_op[counter]) == result[counter]:
    #                     checker[counter] = True
    #                     marks += 2
    #                 else:
    #                     checker[counter] = False
    #                 counter += 1
    #                 os.killpg(os.getpgid(p.pid), signal.SIGTERM)
    #         # print(code)
    #         except:
    #             print('Error')
    #         score_object = Score.objects.get(user_f=current_user, question_f=current_question)
    #         if score_object.score < marks:
    #             current_user.money += (marks - score_object.score)
    #             score_object.score = marks
    #             score_object.save()
    #
    #         # all_marks = list(jsonDec.decode(current_user.score))
    #         current_user.total_score = sum(Score.objects.filter(user_f=current_user).values_list('score', flat=True))
    #         current_user.save()
    #         return render(request, 'round2/question_details.html',
    #                       {'pegs_id': int("3"), 'error_msg': False, 'submitted': True, 'one': 50, 'two': 50,
    #                        'three': 100, 'four': 100, 'submitted_code': code, 'selected_question': current_question,
    #                        'user_id': user_id, 'checker': checker,
    #                        'remaining_time': current_user.end_time - time.time(),
    #                        'bought': True, 'question_id': question_id, 'question_score': score_object.score,
    #                        'money': current_user.money})
    #     else:
    #         print(subprocess.CalledProcessError)
    #         # print(compile_output)
    #
    #         f = open('output.txt', 'w')
    #         f.write(compile_output)
    #         f.close()
    #
    #         return render(request, 'round2/question_details.html',
    #                       {'pegs_id': int("3"), 'submitted': False, 'submitted_code': code,
    #                        'selected_question': current_question,
    #                        'user_id': user_id, 'checker': False,
    #                        'remaining_time': current_user.end_time - time.time(), 'error_msg': str(compile_output)
    #                           , "question_id": question_id, 'bought': True, 'output_to_display':output_to_display})
    #
    #     return HttpResponse("<h2>"+ str(result) +"</h2>")
    # else request.POST.get("run"):


    ''' else :.
            print(subprocess.CalledProcessError)
            print(compile_ouput)

            f = open('output.txt','w')
            f.write(compile_ouput)
            f.close()
            return HttpResponse("<h2>" + compile_ouput + "</h2>")'''


def leaderboard(request, user_id):
    current_user = User.objects.get(pk=user_id)
    # current_user.total_score = 0
    # jsonDec = json.decoder.JSONDecoder()
    # all_marks = list(jsonDec.decode(current_user.score))
    # for marks in all_marks:
    #     current_user.total_score += marks
    # current_user.save()
    all_user = list(User.objects.all().order_by('total_score'))
    all_user.reverse()

    if request.POST.get("finish"):

        return render(request, 'round2/leaderboard_new.html',
                      {'user_id': int(user_id), 'all_user': all_user, 'leaderboard_clicked': False})
    elif request.POST.get("leader"):
        return render(request, 'round2/leaderboard_new.html',
                      {'user_id': int(user_id), 'all_user': all_user, 'leaderboard_clicked': True, 'one': 5, 'two': 5,
                       'three': 10, 'four': 10, 'five': 20})
    else:
        return render(request, 'round2/leaderboard_new.html',
                      {'user_id': int(user_id), 'all_user': all_user, 'leaderboard_clicked': False})


def instruction_view(request, user_id, question_id):
    current_user = User.objects.get(pk=user_id)
    all_users = list(User.objects.all().order_by('total_score'))
    all_users.reverse()
    print(current_user.cnt)
    if current_user.cnt<=3:
    	current_user.cnt += 1
    	current_user.save()
    	return render(request, 'round2/instructions_new.html',
		      {'user_id': user_id, 'question_id':question_id, 'one': 50, 'two': 50, 'three': 100, 'four': 100})
    else:
        return render(request, 'round2/leaderboard_new.html',
                      {'user_id': int(user_id), 'question_id': int(question_id),'all_user': all_users, 'leaderboard_clicked': False})


def add_que(request, user_id):
    user = User.objects.get(pk=user_id)
    if request.POST.get("easy"):
        user.buyed_questions += json.dumps(user.easy_counter)
    return render(request, 'round2/select_questions.html',
                  {'buyed_questions': '', 'user_id': user_id,
                   })

def save_answer(request, user_id, question_id):
	code = request.POST.get("text_area")
	f = open(input_file + '.' + file_extension, 'w')
	# f=open('test.cpp','w')
	f.write(code)
	f.close()
	return render(request, 'round2/question_details.html',
                      {'pegs_id': int("3"), 'error_msg': False, 'submitted': True, 'one': 50, 'two': 50,
                       'three': 100, 'four': 100, 'submitted_code': code, 'selected_question': current_question,
                       'user_id': user_id, 'checker': False, "one_score":score_for_one,
                       'remaining_time': current_user.end_time - time.time(), 'error_msg': errors,
                       'bought': True, 'question_id': question_id, 'question_score': score_object.score,
                       'money': current_user.money, 'language': score_object.language_preferred})
                       

'''def buy_question(request, user_id, question_id):
    user_id = int(user_id)
    question_id = int(question_id)

    current_user = User.objects.get(pk=user_id)
    question = Question.objects.get(pk=question_id)

    error_msg = "You don't have enough money"
    previous_code = ""
    if current_user.money >= question.cost:
        print(question)
        if question.type == "Easy":
            if current_user.easy_counter < 3:
                current_user.easy_counter += 1
            else:
                return HttpResponse("you cant buy more easy question")
        else:
            current_user.easy_counter -= 3

        current_user.money -= question.cost
        current_user.save()
        score = Score(user_f=current_user, question_f=question)
        score.save()
        # question.user.add()
        # question.save()
        # a = question.user.all()

        return HttpResponse("true")
    else:
        return HttpResponse(error_msg)
    # return render(request, 'round2/question_details.html',
    #               {'pegs_id': int("3"), 'selected_question': question, 'user_id': user_id,
    #                'submitted_code': previous_code, 'remaining_time': current_user.end_time - time.time()})'''
    
    
def run_code(p, input):
    print('starting thread')
