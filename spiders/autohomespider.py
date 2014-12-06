#-*- encoding:UTF8 -*-
from spiderframework import ProcessNode
        
class AutohomeEvaluationSpider(ProcessNode):
    u"""
     详细获取
    """
    elems = { 
             'base':'//div[contains(@class,"koubei")]',
             'url':('descendant::span[@class="time"]/a/@href', None, "'re_str':'(http://.*\.html)?.*'"),
             'content':('div', None, None),
                    }
    
#     nextnodes = [('AutohomeEvaluationSpider', ('//a[contains(@class,"item-last")]/@href', \
#                                                None, '"eva_pages":(/"index_{page}.html",1,1), "pre_url":"http://k.autohome.com.cn/"'), False),]
    
    save = {'driver':'mongodb', 'param':{'db':'autohome', 'collection':'deveva', 'connectTimeoutMS':100000}, 'alias':{'url':'_id'}}
    
class AutohomeEvaluationSpiderNextUrl(ProcessNode):
    u"""
     详细获取
    """
    elems = { 
                    }
    
    nextnodes = [('AutohomeEvaluationSpider', ('//a[contains(@class,"item-last")]/@href', \
                                               None, '"eva_pages":(/"index_{page}.html",1,1), "pre_url":"http://k.autohome.com.cn/"'), False),]
   
class AutohomeTotalEvalSpider(ProcessNode):
    u"""
     总评价获取
    """
    elems = {
             'url':('//div[contains(@class,"title-name")]/a/@href', None, None),
             'modelname':('//div[contains(@class,"title-name")]/a/text()',None, None),
             'content':('//dd/ul', None, None),
             'statistic_onsell':('//ul[contains(@id,"specList")]/li[@data-value]', None, "'alle':None")
             }
    save = {'driver':'mongodb', 'param':{'db':'autohome', 'collection':'toteva', 'upsert':True,'connectTimeoutMS':100000}, 'alias':{'url':'_id'}}
    
class AutohomeBrandNode(ProcessNode):
    u"""
     品牌获取
    """
    elems = {
             'base':'//dl[dt]',
             'url':('dt/div/a/@href', None, None),
             'name':('dt/div/a/text()', None, None),
             'subbrands': {
                           'base':'dd/div[contains(@class,"tit")]',
                           'name':('text()', None, None),
                           'models':{
                                  'base':'following::ul[1]/li/h4/a',
                                  'url':('@href', None, "'re_str':'(http://www.autohome.com.cn/\d+/).*'"),
                                  'name':('text()', None, None),
                                  }
                        }
             }
    nextnodes = [(AutohomeTotalEvalSpider, ('dd/ul/li/h4/a/@href', None, \
                                       "'re_str':'(http://www.autohome.com.cn/\d+/).*','str_replace':('www','k')"), False), 
                 (AutohomeEvaluationSpiderNextUrl, ('dd/ul/li/h4/a/@href', None, \
                                       "'re_str':'(.autohome.com.cn/\d+/).*',"+
                                       "'pre_url':'http://k'"), False),
                 ]
    save = {'driver':'mongodb', 'param':{'db':'autohome', 'collection':'brands'}, 'alias':{'url':'_id'}}
    
spiders = [AutohomeBrandNode, AutohomeTotalEvalSpider, AutohomeEvaluationSpiderNextUrl, AutohomeEvaluationSpider, ]

if __name__ == "__main__":
    import pprint
    import argparse
    
    def spider_desc():
        res = u'爬虫名称\t爬虫描述\n'
        for spd in spiders:
            res += '\t'.join((spd.__name__, spd.__doc__))
            res += '\n'
        return res
    
    parser = argparse.ArgumentParser()
    parser.usage = u"{0} [OPTION] URL".format(parser.prog)
    parser.epilog = u'如果没有指定spider，则默认执行整个爬虫流程'
    parser.description = u"执行单一的爬虫节点或整个爬虫流程.  默认列出当前爬虫的信息"
    parser.add_argument('-l', action='store_true', default=True, help=u'爬虫信息列表')
    parser.add_argument('-s', type=str, dest='spider', help=u"爬虫名称，执行单一的爬虫")
    parser.add_argument('-f', type=str, dest='flow', help=u"爬虫名称，执行从此节点开始的爬虫流程")
    parser.add_argument('-u','--url', type=str, help=u"爬虫的url", )
    
    args = parser.parse_args()
    if getattr(args, 'spider', ''):
        if args.spider not in [x.__name__ for x in spiders]:
            print(u'不存在爬虫{0}'.format(args.spider))
            print(u'\n爬虫列表如下:')
            print(spider_desc())
        else:
            spider = getattr(__import__('__main__'), args.spider)(args.url)
            res = spider.process()
            if res:
                for x in res:
                    pprint.pprint(x)
    elif getattr(args, 'flow', ''):
        spider = spiders[0](args.url)
        res = spider.pipeline_process()
        if res:
            for x in res:
                pprint.pprint(x)
    else:
        print(spider_desc())