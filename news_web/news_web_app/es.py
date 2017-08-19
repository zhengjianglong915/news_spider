#coding=utf-8
import urllib 
import urllib2 
import json
import logging
import sys
import re
import traceback

type = sys.getfilesystemencoding()

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='es.log',
    filemode='a')

class ES(object):
    def __init__(self):
        self.IP = "localhost"
        self.PORT = "9200"
        pass

    def article_search_list(self, search_condition, key=None, DB="articles_testN"):
        try:
            # 来源网站
            article_source = search_condition['article_source']
            # 是否重复
            article_db = search_condition['article_db']
            # 标注状态
            article_label_state = search_condition['article_label_state']
            # 开始时间
            startTime = search_condition['startTime']
            # 结束时间
            endTime = search_condition['endTime']
            # 当前页
            current_page = search_condition['current_page']
            # 每页显示的页数
            page_size = search_condition['page_size']
            # 类标
            article_label = search_condition['article_label']
            # 标签
            tags = search_condition['tags']

            timerange_check = search_condition["timerange_check"]

            print "es tags:",tags
        
            query_filter = []
            if timerange_check == 1:
                query_filter.append({ "range" : 
                    {
                     "article_publish_time" :  # 发布时间
                        {
                            "gte" :startTime,
                            "lte" :endTime
                        }
                    }
                })   

            if article_db == 1:
                query_filter.append({ "term":{ "is_repeate":"0"}})     

            
            if len(article_source) != 0:
                should_query = []
                for source in article_source:
                    should_query.append({ "match_phrase":{"article_source":source}})
                query_filter.append({"bool":{"should":should_query}})

            if len(article_label_state) != 0:
                should_query = []
                for label_state in article_label_state:
                    should_query.append({ "term":{"article_label_state":label_state}})
                query_filter.append({"bool":{"should":should_query}})

            if len(article_label) != 0:
                should_query = []
                for label in article_label:
                    should_query.append({ "term":{"article_label":label}})
                query_filter.append({"bool":{"should":should_query}})

            should_query2 = []
            if len(tags) != 0:
                for tag in tags:
                    should_query2.append({ "match_phrase":{"tags":tag}})
                query_filter.append({"bool":{"should":should_query2}})

            if key != None and key != "":
                query_filter.append({
                    "query_string" : {
                        "fields" : ["article_title", "article_content"],
                        "query" : key,
                        "default_operator":"AND"
                    }
                })

            bool_query = {"must":query_filter}    
            mutli_query = {
              "query":{"bool":bool_query},
              "highlight": {
                    "fields" : {
                        "article_content" : {"fragment_size" : 240},
                        "article_title": {}
                    }
                }
              #"sort": { "article_publish_time": { "order": "asc" }} 
            }
            
            print "mutli_query:",mutli_query
            sizefrom  = int(page_size) * int(current_page)
            url = "http://" + self.IP + ":" + self.PORT + "/news_spider_db/" \
               + DB + "/_search?size=" + str(page_size)+ "&from=" +str(sizefrom)

            #print "url:",url
            #print "mutli_query:",mutli_query
            result = self.get(url, mutli_query)

            article_list = []
            if result is None:
                return article_list

            for line in result:
                #print line
                _id = line['_id']
                article = line["_source"]
                article['id'] = _id
                #print _id
                if key != None and key != "":
                    highlight = line['highlight']
                    #print highlight

                    if highlight.has_key('article_content'):
                        highlight['article_content'] = highlight['article_content'][0]
                        #print highlight['article_content']
                        #print "--------------------------------"
                        highlight['article_content'] = highlight['article_content'].replace("<em>","######")
                        highlight['article_content'] = highlight['article_content'].replace("</em>","@@@@@@")
                        highlight['article_content'] = self._remove_htmlTags(highlight['article_content'])
                        highlight['article_content'] = highlight['article_content'].replace("######", "<em>")
                        highlight['article_content'] = highlight['article_content'].replace("@@@@@@", "</em>")
                        article['article_content'] = highlight['article_content']
                    else:
                        article['article_content'] = self._remove_htmlTags(article['article_content'])

                    article['article_content'] = article['article_content'][0: 240]

                    if highlight.has_key('article_title'):
                        article['article_title'] = highlight['article_title'][0] 
                else:
                    article['article_content'] = self._remove_htmlTags(article['article_content'])
                    article['article_content'] = article['article_content'][0: 240]
                    
                article_list.append(article)
                #print line["_source"]
            return article_list
        except BaseException, e:
            logging.error(e)
            print e
            print traceback.print_exc()
            return []


    def article_simple_search(self, search_condition, key=None, DB="articles_testN"):
        try:
            # 当前页
            current_page = search_condition['current_page']
            # 每页显示的页数
            page_size = search_condition['page_size']
            bool_query = {}
            mutli_query_with_key = {
                "query": {
                    "query_string" : {
                        "fields" : ["article_title", "article_content"],
                        "query" : key,
                        "default_operator":"AND"
                    }
                },
                "highlight": {
                    "fields" : {
                        "article_content" : {"fragment_size" : 240},
                        "article_title": {}
                    }
                }
            }

            mutli_query_without_key = {
              "query": { 
                "bool": bool_query
              }
              #"sort": { "article_publish_time": { "order": "asc" }} 
            }

            # 关键词
            if key != None and key != "":
                mutli_query = mutli_query_with_key
            else:
                mutli_query = mutli_query_without_key
           
            sizefrom  = int(page_size) * int(current_page)
            url = "http://" + self.IP + ":" + self.PORT + "/news_spider_db/" \
               + DB + "/_search?size=" + str(page_size)+ "&from=" +str(sizefrom)
            result = self.get(url, mutli_query)
            article_list = []
            if result is None:
                return article_list
            for line in result:
                #print line
                _id = line['_id']
                article = line["_source"]
                article['id'] = _id
                #print _id
                if key != None and key != "":
                    highlight = line['highlight']
                    #print highlight
                    if highlight.has_key('article_content'):
                        highlight['article_content'] = highlight['article_content'][0]
                        #print highlight['article_content']
                        highlight['article_content'] = highlight['article_content'].replace("<em>","######")
                        highlight['article_content'] = highlight['article_content'].replace("</em>","@@@@@@")
                        highlight['article_content'] = self._remove_htmlTags(highlight['article_content'])
                        highlight['article_content'] = highlight['article_content'].replace("######", "<em>")
                        highlight['article_content'] = highlight['article_content'].replace("@@@@@@", "</em>")
                        article['article_content'] = highlight['article_content']
                    else:
                        article['article_content'] = self._remove_htmlTags(article['article_content'])

                    article['article_content'] = article['article_content'][0: 240]

                    if highlight.has_key('article_title'):
                        article['article_title'] = highlight['article_title'][0]
                else:
                    article['article_content'] = self._remove_htmlTags(article['article_content'])
                    article['article_content'] = article['article_content'][0: 240]
                    
                article_list.append(article)
                #print line["_source"]
            return article_list
        except BaseException, e:
            logging.error(e)
            print e
            print traceback.print_exc()
            return []

    def _remove_htmlTags(self, html):
        # tag
        tag_re = re.compile(r'<[^>]+>',re.S)
        result = tag_re.sub('', html)

        ## space 
        space_re = re.compile(r'&[^>]+;', re.S)
        result = space_re.sub('', result)
        return result
    

    def get(self, url, values):
        try:
            # 对数据进行JSON格式化编码
	    jdata = json.dumps(values) 
	    # 生成页面请求的完整数据
            req = urllib2.Request(url, jdata)
            # 发送页面请求 
            response = urllib2.urlopen(req) 
            # 获取服务器返回的页面信息
            the_page = response.read()
            result = json.loads(the_page)
            return  result['hits']['hits']
        except BaseException, e:
            logging.error(e) 
            return None          

    
    def put(self, url, values):
        try:
           # 对数据进行JSON格式化编码
           jdata = json.dumps(values)
           # 生成页面请求的完整数据
           req = urllib2.Request(url, jdata)
           req.add_header('Content-Type', 'your/contenttype')
           req.get_method = lambda: 'PUT'
           response = urllib2.urlopen(req)
           result = json.loads(response.read())
           return result
        except BaseException, e:
            logging.error(e)
            logging.error("url:"+url)
            #logging.error("values:"+str(values))
            logging.error("-----")
            return None       

#es = ES()
#print es.get("http://localhost:9200/news_spider_db/articles_testP/_search",{"query":{"match":{"simhash":"1855271740191983003"}}})
#print es.put("http://localhost:9200/news_spider_db/articles_testN/1",{"name":"zjl"})



#search_condition={"startTime":"1999-01-03","endTime":"2018-01-03","page_size":5,\
# "current_page":0, "article_db":1, "article_label_state":1,"article_source":["新浪网","凤凰网"]}

#print es.article_key_search(search_condition,"全民公决")
