from django.conf.urls import include, url
from django.contrib import admin
from news_web_app import views as news_web_view

 
urlpatterns = [
    url(r'^$', news_web_view.login, name='login'),
    url(r'^index/$', news_web_view.index, name='index'),
    url(r'^search', news_web_view.search, name='search'),
    url(r'^logining', news_web_view.logining, name='logining'),
    url(r'^test', news_web_view.test, name='test'),
    url(r'^taglist/$', news_web_view.taglist, name='taglist'),
    url(r'^userlist/$', news_web_view.userlist, name='userlist'),
    url(r'^adduser', news_web_view.adduser, name='adduser'),
    url(r'^deluser/$', news_web_view.deluser, name='deluser'),
    url(r'^logout/$', news_web_view.logout, name='logout'),
    url(r'^page/$', news_web_view.page, name='page'),
    url(r'^addTag', news_web_view.addTag, name='addTag'),
    url(r'^delTag', news_web_view.delTag, name='delTag'),
    url(r'^addArticleTag', news_web_view.addArticleTag, name='addArticleTag'),
    url(r'^removeArticleTag', news_web_view.removeArticleTag, name='removeArticleTag'),
    url(r'^changeLabel', news_web_view.changeLabel, name='changeLabel'),
    url(r'^approval', news_web_view.approval, name='approval'),
    url(r'^system_setting_page', news_web_view.system_setting_page, name='system_setting_page'),
    url(r'^system_setting', news_web_view.system_setting, name='system_setting'),
    url(r'^admin/', include(admin.site.urls)),
]
