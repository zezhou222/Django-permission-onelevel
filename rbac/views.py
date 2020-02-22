import json

from django.contrib import auth
from django.http import HttpResponse
from django.shortcuts import render, redirect

from rbac.models import (
    UserInfo,
    Role,
    Path,
    Menu
)


def Register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        dic = request.POST.dict()
        # 先查看该用户名是否已经存在
        ret = UserInfo.objects.filter(username=dic.get('username')).first()
        if not ret:
            # 创建用户数据，返回的用户对象
            obj = UserInfo.objects.create_user(**dic)
            # 关联初始权限
            role_id = Role.objects.get(role_name='普通用户').id
            UserInfo.objects.get(id=obj.id).role.set((role_id,))
            return redirect('/login/')
        else:
            return HttpResponse(content='the username exists.', status=422)


def Login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        dic = request.POST.dict()
        # 认证成功，返回对象
        ret = auth.authenticate(request, **dic)
        if ret:
            # 认证成功，添加session,中间件判断是否登陆
            auth.login(request, ret)
            # 添加权限路径准备工作
            """
            [
                {
                    "menu": "图书管理", 
                    "request_path": "/book_page/",
                    "path": [
                        {"method": "get", "auth_path": "/book/", "alias": "get_books"}, 
                        {"method": "post", "auth_path": "/book/", "alias": "add_book"}
                    ]
                },
                {
                    "menu": "学生管理", 
                    "request_path": "/student_page/",
                    "path": [
                        {"method": "get", "auth_path": "/student/", "alias": "get_students"}, 
                        {"method": "post", "auth_path": "/student/", "alias": "add_student"}
                    ]
                },
            ]
            """
            all_path_data = []
            # 查询用户都有什么角色
            role_data = UserInfo.objects.get(username=request.user.username).role.all().values()
            for dic in role_data:
                # 通过角色id查看角色都有什么访问权限
                path_obj = Role.objects.get(id=dic["id"]).path.all()
                for obj in path_obj:
                    # 获取路径的菜单名
                    menu_name = obj.menu.menu_name
                    request_path = obj.menu.request_path
                    is_name = obj.menu.is_menu
                    # 获取菜单下的认证路径
                    temp_path = {"method": obj.method, "auth_path": obj.auth_path, "alias": obj.alias}
                    # 添加菜单名，及路径
                    for dic in all_path_data:
                        # 菜单名存在，则直接添加认证路径
                        if dic["menu"] == menu_name:
                            dic["path"].append(temp_path)
                            break
                    else:
                        # 不存在，则添加初始数据
                        all_path_data.append({"menu": menu_name, "request_path": request_path, "is_menu": is_name, "path": [temp_path]})
            # print(all_path_data)
            # 添加权限路径到session
            request.session["auth"] = all_path_data
            # 重定向到首页
            return redirect('/index/')
        else:
            return HttpResponse(content='username or password error.', status=401)


def Logout(request):
    auth.logout(request)
    return HttpResponse(content='logout success')


def Permission(request):
    return render(request, 'permission.html')


def MyUser(request):
    if request.method == 'GET':
        id = request.GET.get('id', None)
        if not id:
            page = int(request.GET.get('page'))
            limit = int(request.GET.get('limit'))
            if page-1 == 0:
                objs = UserInfo.objects.all()[0:limit]
            else:
                objs = UserInfo.objects.all()[(page-1)*limit:page*limit]
            values = list(objs.values('id', 'username'))
        else:
            id = int(id)
            result = UserInfo.objects.filter(id=id).values('id', 'username', 'role__id', 'role__path__id')
            values = {"id": '', "username": '', "role_id": [], "path_id": []}
            for dic in result:
                if values['id'] == '':
                    values['id'] = dic['id']
                    values['username'] = dic['username']
                if dic['role__id'] not in values["role_id"]:
                    values["role_id"].append(dic['role__id'])
                if dic['role__path__id'] not in values["path_id"]:
                    values["path_id"].append(dic['role__path__id'])
        return HttpResponse(json.dumps(values), content_type='application/json')

    elif request.method == 'POST':
        pass
    elif request.method == 'PUT':
        pass
    elif request.method == 'DELETE':
        pass


def MyRole(request):
    if request.method == 'GET':
        id = request.GET.get('id', None)
        if not id:
            objs = Role.objects.all()
            values = list(objs.values('id', 'role_name'))
        else:
            id = int(id)
            result = Role.objects.filter(id=id).values('id', 'role_name', 'path__id')
            values = {"id": '', "role_name": '', "path_id": []}
            for dic in result:
                if values['id'] == '':
                    values['id'] = dic['id']
                    values['role_name'] = dic['role_name']
                if dic['path__id'] not in values["path_id"]:
                    values["path_id"].append(dic['path__id'])
        return HttpResponse(json.dumps(values), content_type='application/json')

    elif request.method == 'POST':
        pass
    elif request.method == 'PUT':
        opt = request.GET.get('opt', None)
        # 更新用户选择得角色
        if opt == 'save_role':
            content = json.loads(request.body)
            user_id = content.get('user_id')
            role_ids = content.get('role_ids')
            UserInfo.objects.get(id=user_id).role.set(role_ids)
        else:
            # 更新角色信息
            pass
        return HttpResponse(json.dumps(0), content_type='application/json')
    elif request.method == 'DELETE':
        pass


def MyMenu(request):
    if request.method == 'GET':
        values = Path.objects.all().values('id', 'path_name', 'menu_id', 'menu__menu_name', 'menu__is_menu')
        data = []
        for dic in values:
            # if not dic['menu__is_menu']:
            #     continue

            temp = {"path_id": dic["id"], "path_name": dic["path_name"]}
            for menu_dic in data:
                if dic["menu__menu_name"] == menu_dic["menu_name"]:
                    menu_dic["path"].append(temp)
                    break
            else:
                data.append({"menu_id": dic["menu_id"], "menu_name": dic["menu__menu_name"], "path": [temp]})
        return HttpResponse(json.dumps(data), content_type='application/json')

    elif request.method == 'POST':
        pass
    elif request.method == 'PUT':
        opt = request.GET.get('opt', None)
        # 更新用户选择得角色
        if opt == 'save_permission':
            content = json.loads(request.body)
            role_id = content.get('role_id')
            permission_ids = content.get('permission_ids')
            Role.objects.get(id=role_id).path.set(permission_ids)
        else:
            # 更新权限信息
            pass
        return HttpResponse(json.dumps(0), content_type='application/json')
    elif request.method == 'DELETE':
        pass
