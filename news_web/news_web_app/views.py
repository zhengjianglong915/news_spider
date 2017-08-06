#coding=utf-8
#from user_dao import UserDAO
import sys
import os
import json  
from es import ES
from django.http import HttpResponse 
from django.views.decorators.csrf import csrf_exempt
import pdb

mongodb_path = os.path.join(os.path.dirname(__file__),os.pardir,os.pardir)
sys.path.append(mongodb_path)
from news_mongodb.tags_dao import TagsDAO
from news_mongodb.user_dao import UserDAO
from news_mongodb.article_dao import ArticleDAO
from news_mongodb.system_setting import SystemSetting
from news_mongodb.models.user import User
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect
import logging

labelMap={"1":"articles_testP", "0":"articles_testN"}

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='news_web.log',
    filemode='a')
 

def login_interceptor(func):
    def login_wrapper(request):
        user = request.session.get('user',default=None)
        #print user
        #return func(request)
	if user:
	    return func(request)
	else:
	    return render(request, 'login.html')
    return login_wrapper

def admin_interceptor(func):
    def wrapper(request):
	user = request.session.get('user',default=None)
	if user and user['role'] == '0':
	    return func(request)
	else:
	    return render(request, 'index.html')
    return wrapper

def test(request):
    return render(request, 'login.html')

def login(request):
    #return render(request,"maintain.html")
    return render(request, 'login.html')

@csrf_exempt
def logining(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
        user = User()
        user.username = username
        user.password = password
        print username
        print password
        userDAO = UserDAO()
        user = userDAO.login(user)
        print user
        if user:
            user['id'] = user['_id']
            request.session['user'] = user
            return HttpResponseRedirect("/index")
        return render(request, 'login.html')

    except BaseException, e:
        logging.error(e)
        return render(request, 'login.html')

@login_interceptor
def index(request):

    #print "index "
    tagDAO = TagsDAO()
    tagList = tagDAO.tagList()
    #print tagList
    return render(request, 'index.html', {
     "current_page":0, "webs":["xlw","rmw","zhw"], "page_size": 20,"tagList":json.dumps(tagList),"tagList2":tagList})


@csrf_exempt
@login_interceptor
def search(request):
    try:
        logging.info("search(request)")
        #pdb.set_trace()
        # 当前页
        if 'current_page' in request.POST:
            current_page = int(request.POST['current_page'])
        else:
            current_page = 0
        
        # 文章抓取网站
        webMap = {"xlw":"新浪网", "xhs":"新华社","fhw":"凤凰网"} #"rmw":"人民网","zhw":"中华网",
        if 'webs' in request.POST:
            str_webs = request.POST['webs']
            str_webs = str_webs.split(",")
            webs = []
            for i in range(len(str_webs)):
                key = str_webs[i]
                webs.append(webMap[key])
        else:
            webs = ["新浪网","新华网","凤凰网"] #"人民网", "中华网",
            str_webs = ["xlw","xhs","fhw"] #"rmw","zhw",

        # 标签
        if "tags" in request.POST:
            str_tags = request.POST['tags']
            print str_tags
            tags = str_tags.split(",")
        else:
            tags = []

        if '' in tags:
            tags.remove('')
        print "tags:",tags

      
        # 每页显示的页数
        if "page_size" in request.POST:
            page_size = request.POST['page_size']
            page_size = int(page_size)
        else:
            page_size = 20

        if "timerange" in request.POST:
            timerange = request.POST['timerange']
            timerange = timerange.split(" - ")
            startTime = timerange[0]
            endTime = timerange[1]
        else:
            startTime = '2017-01-11'
            endTime = '2017-01-15'
            timerange = startTime + " - " + endTime

        # 是否去重
        if "article_db" in request.POST:
            article_db = request.POST['article_db']
            article_db = int(article_db)
        else:
            article_db = 0

        if "label_state" in request.POST:
            label_state = request.POST['label_state']
            label_state = int(label_state)
        else:
            label_state = 0


        if "label" in request.POST:
            label = request.POST['label']
        else:
            label = "1"

        if "search_key" in request.POST:
            search_key = request.POST['search_key'].strip()
        else:
            search_key = None

        if "search_type" in request.POST:
            search_type = request.POST['search_type'].strip()
        else:
            search_type = "simple_search"

        print "search_key:",search_key
        print "search_type",search_type
        #label = labelMap[label]
        
        user = request.session.get('user',default=None)
        if label_state == 1 and user['role'] == "1":
            condition = {"article_source":webs, "article_db":article_db, "article_label_state":label_state, "startTime": startTime,
             "endTime":endTime, "current_page":current_page , "page_size":page_size,"update_student":user["username"],"article_label":label,"tags":tags}
        else:
            condition = {"article_source":webs, "article_db":article_db, "article_label_state":label_state, "startTime": startTime,
             "endTime":endTime, "current_page":current_page , "page_size":page_size,"article_label":label,"tags":tags}
        
        logging.info("[search] condition=" + str(condition))
        
        system_setting = SystemSetting()
        databases = system_setting.get("databases", "mongodb")
        print "databases:",databases
        if databases == 'es':
            es = ES()
            if search_type == "simple_search":
                articleList = es.article_simple_search(condition, search_key)
            else:
                articleList = es.article_search_list(condition, search_key)
        else:
            articleDAO = ArticleDAO('articles_testN')
            articleList = articleDAO.article_search_list(condition)

        logging.info("[search] len(result)=" + str(len(articleList)))
    except BaseException, e:
        logging.error(e)
        articleList = []

    return HttpResponse(json.dumps(articleList), content_type="application/json")  

@login_interceptor
@admin_interceptor
def userlist(request):
    userDAO = UserDAO()
    userList = userDAO.userlist()
    return render(request, 'userList.html', {'userList':userList})


@csrf_exempt
@login_interceptor
@admin_interceptor
def adduser(request):

    username = request.POST['username']
    password = request.POST['password']

    role = request.POST['role']
    user = User()
    user.username = username
    user.password = password
    user.role = role
    userDAO = UserDAO()

    flag = userDAO.addUser(user)
    if flag:
    	message = "添加成功"
    else:
    	message = "添加失败"
    userList = userDAO.userlist()
    return render(request, 'userList.html', {"message": message,
    	'userList':userList})

@login_interceptor
@admin_interceptor
def deluser(request):

    userId = request.GET['userId']
    userDAO = UserDAO()
    flag = userDAO.deluser(userId)
    if flag:
    	message = "删除成功"
    else:
    	message = "删除失败"

    userList = userDAO.userlist()
    return render(request, 'userList.html', {"message": message,
    	'userList':userList})

@login_interceptor
def logout(request):
    del request.session['user']
    return render(request, 'login.html')

@login_interceptor
def page(request):
    try:
        article_id = request.GET["articleId"]
        label = request.GET['label']
        #label = labelMap[label]
        articleDAO = ArticleDAO('articles_testN')
        article = articleDAO.show_article(article_id)
        return render(request, 'page.html', {'article': article})
    except BaseException, e:
        logging.error(e)
        return render(request, 'error.html')


@login_interceptor
@admin_interceptor
def taglist(request):
    try:
        tagDAO = TagsDAO()
        tagList = tagDAO.tagList()
        return render(request, 'tags.html',{"tagList":tagList})
    except BaseException, e:
        logging.error(e)
        return render(request, 'error.html')
    

@csrf_exempt
@login_interceptor
@admin_interceptor
def addTag(request):
    try:
        tag = request.POST['tag']
        tagDAO = TagsDAO()
        tagDAO.addTag(tag)
        tagList = tagDAO.tagList()
        return render(request, 'tags.html',{"tagList":tagList})
    except BaseException, e:
        logging.error(e)

@login_interceptor
@admin_interceptor
def delTag(request):
    try:
        tagId = request.GET['id']
        tagDAO = TagsDAO()
        tagDAO.delTag(tagId)
        tagList = tagDAO.tagList()
        return render(request, 'tags.html',{"tagList":tagList})
    except BaseException, e:
        logging.error(e)


@login_interceptor
def addArticleTag(request):
    try:
        article_id = request.GET['article_id']
        label = request.GET['label']
        tag = request.GET['tag']
        #label = labelMap[label] ####
        articleDAO = ArticleDAO('articles_testN')
        flag = articleDAO.addTag(article_id, tag)
        if flag:
            message = "success"
        else:
            message = "failed"
        return HttpResponse(json.dumps(message), content_type="application/json")
    except BaseException, e:
        logging.error(e)
        return HttpResponse(json.dumps("failed"), content_type="application/json")

@login_interceptor
def removeArticleTag(request):
    try:
        article_id = request.GET['article_id']
        label = request.GET['label']
        tag = request.GET['tag']
        #label = labelMap[label] ####
        print "removeArticleTag"
        articleDAO = ArticleDAO('articles_testN')
        flag = articleDAO.removeTag(article_id, tag)
        if flag:
            message = "success"
        else:
            message = "failed"
        return HttpResponse(json.dumps(message), content_type="application/json")
    except BaseException, e:
        logging.error(e)
        return HttpResponse(json.dumps("failed"), content_type="application/json")


@login_interceptor
def changeLabel(request):
    try:
        article_id = request.GET['article_id'].strip()
        label = request.GET['label']
        reverseMap={"0":"1", "1":"0"}
        rLabel = reverseMap[label]
        logging.info("[changeLabel] article_id=" +article_id +" label=" \
            + label + "  rLabel=" + rLabel)
        
        #label = labelMap[label] 
        #reverseLabel = labelMap[reverseLabel]
        articleDAO = ArticleDAO('articles_testN')
        article = articleDAO.show_article(article_id)
        article.pop("_id")
        article.pop("id")
        article['article_label'] = int(rLabel)
        user = request.session.get('user',default=None)

        if user['role'] == "0":
            article['article_label_state'] = 2
            article['update_admin'] = user['username']
        elif user['role'] == "1":
            article['article_label_state'] = 1
            article['update_student'] = user['username']
        
        #article['article_label_state'] = 0
        result = articleDAO.update_article(article_id, article)
        logging.info("[changeLabel] result=" + str(result))
        if result:
            return HttpResponse(json.dumps('{"label":"'+str(rLabel)+'","article_id":"'+str(article_id)+'"}'),
         content_type="application/json")
        else:
            return HttpResponse(json.dumps('{"label":"failed"}'), content_type="application/json")
    except BaseException, e:
        logging.error(e)
        return HttpResponse(json.dumps('{"label":"failed"}'), content_type="application/json")

@login_interceptor
def approval(request):
    ## 审核
    try:
        article_id = request.GET['article_id'].strip()
        label = request.GET['label']
        label = labelMap[label] 
        articleDAO = ArticleDAO('articles_testN')
        article = articleDAO.show_article(article_id)
        article.pop("id")
        article.pop("_id")
        user = request.session.get('user',default=None)
        if user['role'] == "0":
            article['article_label_state'] = 2
            article['update_admin'] = user['username']
        elif user['role'] == "1":
            article['article_label_state'] = 1
            article['update_student'] = user['username']
        
        #article['article_label_state'] = 0
        result = articleDAO.update_article(article_id, article)
        if result:
            return HttpResponse(json.dumps("success"),content_type="application/json")
        else:
            return HttpResponse(json.dumps("failed"),content_type="application/json")
    except BaseException, e:
        logging.error(e)
        return HttpResponse(json.dumps("failed"),content_type="application/json")


@login_interceptor
@admin_interceptor
def system_setting_page(request):
    system_setting = SystemSetting()
    databases = system_setting.get("databases", "mongodb")
    #系统设置页面
    return render(request, 'system_setting.html',{"databases":databases})

@csrf_exempt
@login_interceptor
@admin_interceptor
def system_setting(request):
    if "databases" in request.POST:
        databases = request.POST['databases']
    else:
        databases = "mongodb"

    system_setting = SystemSetting()
    system_setting.put("databases", databases)

    #系统设置页面
    return render(request, 'system_setting.html',{"message":"保存成功",
        "databases":databases})



        


