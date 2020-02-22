import json
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    if request.method == 'GET':
        menu = []
        for dic in request.session["auth"]:
            if dic['is_menu']:
                temp = dic
                temp.pop('path')
                menu.append(temp)
        return render(request, 'index.html', {"menu": menu})


def get_student_page(request):
    operation_alias = []
    auth = request.session["auth"]
    for menu_dic in auth:
        if not menu_dic["is_menu"]:
            continue
        for dic in menu_dic["path"]:
            operation_alias.append(dic["alias"])
    return render(request, 'student.html', {"operation_alias": operation_alias})


def get_book_page(request):
    return render(request, 'book.html')


def student(request):
    if request.method == 'GET':
        student_list = [[1, 'zezhou'], [2, 'lyh']]
        return HttpResponse(json.dumps(student_list), content_type='application/json')
    elif request.method == 'POST':
        return HttpResponse('add student.')
    elif request.method == 'PUT':
        return HttpResponse('update student.')
    elif request.method == 'DELETE':
        return HttpResponse('delete student.')


def book(request):
    if request.method == 'GET':
        book_list = [[1, '海贼王'], [2, '火影忍者'], [3, '死神']]
        return HttpResponse(json.dumps(book_list), content_type='application/json')
    elif request.method == 'POST':
        return HttpResponse('add book.')
    elif request.method == 'PUT':
        return HttpResponse('update book.')
    elif request.method == 'DELETE':
        return HttpResponse('delete book.')
