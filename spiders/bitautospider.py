#-*- encoding: UTF8 -*- 
from spiderframework import ProcessNode
 
 
class BitautoNEvaluationSpider(ProcessNode):
    """
    """
    elems = { 
             'base':'//div[contains(@class,"user_kb")]/dl',
             'url':('descendant::div[@class="tit"]/a/@href', None, '"pre_url":"http://car.bitauto.com"'),
             'total_eva':('//div[contains(@class,"car_info")]/h1/a/@href', None, \
                          '"pre_url":"http://car.bitauto.com"'),
             'detail_eva':('dd', None, None),
                    }
    save = {'driver':'mongodb', 'param':{'db':'a', 'collection':'deveva', 'connectTimeoutMS':100000}, 'alias':{'url':'_id'}}
    
class BitautoEvaluationSpider(ProcessNode):
    """
    """
    elems = { 
             'base':'//div[contains(@class,"user_kb")]/dl[1]',
             'url':('descendant::div[@class="tit"]/a/@href', None, '"pre_url":"http://car.bitauto.com"'),
             'total_eva':('//div[contains(@class,"car_info")]/h1/a/@href', None, \
                          '"pre_url":"http://car.bitauto.com"'),
             'detail_eva':('dd', None, None),
                    }
    save = {'driver':'mongodb', 'param':{'db':'a', 'collection':'deveva', 'connectTimeoutMS':100000}, 'alias':{'url':'_id'}}
    nextnodes = [(BitautoNEvaluationSpider, ('//div[contains(@class,"pages")]/div/a[@href][last()-1]/@href', None, \
                                              '"pre_url":"http://car.bitauto.com","eva_pages":("gengduo/page{page}/",1,1)'), False),]
   
class BitautoTotalEvalSpider(ProcessNode):
    """
    """
    save = {'driver':'mongodb', 'param':{'db':'a', 'collection':'toteva', 'upsert':True,'connectTimeoutMS':100000}, 'alias':{'url':'_id'}}
    elems = {
             'url':('//div[contains(@class,"car_info")]/h1/a/@href', None, '"pre_url":"http://car.bitauto.com"'),
             'modelname':('//h1/a/text()',None, None),
             'total_eva':('//div[contains(@class,"koubei")]/div[2]/ul|//div[@class="col-con"]/div[2]', None,
                          "'join':'','pre_str':'<div>','post_str':'</div>'"),
             }
    
class BitautoSeriesNode(ProcessNode):
    """
    """
    elems = {
             'models':{
                       'base':'//div[contains(@id,"MasterSerialList_0")]/ul/li/div[@class="title"]/a',
                       'url':('@href', None, '"pre_url":"http://car.bitauto.com"'),
                       'name':('text()', None, None),
                            }
             }
    save = {'driver':'mongodb', 'param':{'db':'a', 'collection':'models'}, 'alias':{'url':'_id'}}
    nextnodes = [(BitautoTotalEvalSpider, ('@href', None, "'pre_url':'http://car.bitauto.com', 'post_str':'koubei/'"), False), 
                 (BitautoEvaluationSpider, ('@href', None, "'pre_url':'http://car.bitauto.com', 'post_str':'koubei/gengduo/'"), False),]
    
class BitautlBrandNode(ProcessNode):
    """
    """
    elems = {
             'base':'//ul[contains(@class,"list")]/li/a[2]',
             'url':('@href', None, None),
             'name':('text()', None, None)
             }
    nextnodes = [(BitautoSeriesNode, ('@href', None, None), True), ]
    
spiders = [BitautlBrandNode, BitautoSeriesNode, BitautoTotalEvalSpider, BitautoEvaluationSpider, BitautoNEvaluationSpider,]

if __name__ == "__main__":
#     import pprint
#     
#     spiders = ['BitautlBrandNode', 'BitautoSeriesNode', 'BitautoTotalEvalSpider', 'BitautoEvaluationSpider', 'BitautoNEvaluationSpider']
#     
#     import argparse
#     parser = argparse.ArgumentParser()
#     parser.usage = u"{0} [OPTION] URL".format(parser.prog)
#     parser.epilog = u'如果没有指定spider，则默认执行整个爬虫流程'
#     parser.description = u"执行单一的爬虫节点或整个爬虫流程."
#     parser.add_argument('-s', type=str, dest='spider', choices=spiders, help=u"爬虫名称，执行单一的爬虫")
#     parser.add_argument('url', type=str, help=u"爬虫的url", )
#     
#     args = parser.parse_args()
#     if getattr(args, 'spider', ''):
#         if args.spider not in spiders:
#             print parser.usage
#         else:
#             spider = getattr(__import__('__main__'), args.spider)(args.url)
#             res = spider.process()
#             if res:
#                 for x in res:
#                     pprint.pprint(x)
#     else:
#         spider = getattr(__import__('__main__'), spiders[0])(args.url)
#         res = spider.pipeline_process()
#         if res:
#             for x in res:
#                 pprint.pprint(x)

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
    spider_name = getattr(args, 'spider', '') or getattr(args, 'flow', '')
    if spider_name:
        if spider_name not in [x.__name__ for x in spiders]:
            print(u'不存在爬虫{0}'.format(spider_name))
            print(u'\n爬虫列表如下:')
            print(spider_desc())
        else:
            spider = getattr(__import__('__main__'), spider_name)(args.url)
            if getattr(args, 'spider', ''):
                res = spider.process()
                if res:
                    for x in res:
                        pprint.pprint(x)
            else:
                res = spider.pipeline_process()
                if res:
                    for x in res:
                        pprint.pprint(x)
    else:
        print(spider_desc())