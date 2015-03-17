#-*- encoding:utf-8 -*-
##
# crawl evaluation information of bitauto.com
##
import ast
# import logging as log
import inspect
import importlib
import sys
import socket
from inspect import isclass

import requests
from lxml import html

from spiderflow import Field, log
from spiderflow import processors

from spiderflow.exceptions import DownloadError

# set max recursion number
sys.setrecursionlimit(3000) 

def import_class(name):
    if '.' in name:
        modulestr, classtr = name.rsplit('.', 1)
        return getattr(importlib.import_module( modulestr), classtr)
        # return getattr(__import__(modulestr),classtr)
    else:
        return __import__(name)

class AtomicSpiderBase(object):
    """
    爬虫基础类，职责: 内容的解析
    
    Attribute: 
        elems:{
                ['base': <xpath>,]
                ['field_name':(<xpath>, <regex>, <process>)|subelem,...] 
                                    }
            subelem:{'field_name':elems}
            field_name: field name that defined in ``Item``
            xpath: xpath语法字符串|None(base不能为空.表示base获取的文档树）
            regex: 正则表达式字符串|None
            process: [<func>,...]|None
            func:[func_name[:param,...];...]. 元素的处理分为两个过程，1) 返回元素列表选取处理;2)字符串处理
    """
    elems = {}
    
    # 如果为空则自动识别获取内容后的编码
    content_encode = None
    
    logger = log.getLogger('spider')
    
    def __init__(self, url, item=None):
        """
        @param item: an Item instance or factory function of item
        """
        self._url = url
        self.item = item
        self.logger.log(log.INFO, "Start spider {0} with url {1}".format(
                                    self.__class__.__name__, self._url))

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    def download(self):
        try:
            req = requests.get(self.url, timeout=10)
            return req.content.decode(self.content_encode) \
                if self.content_encode else req.text
        except requests.exceptions.RequestException, e:
            raise DownloadError(e.message)
        except socket.error, e:
            raise DownloadError(e.message)

    def get_item(self):
        fields = dict([(f,Field()) for f in self.elems.keys() if f!='base'])
        #itemname = self.__class__.__name__+'ItemClass'
        if not self.item:
            return fields 
        else:
            if len(set(fields.keys()) - set(self.item.keys())) \
                != len(fields.keys()):
                raise ValueError('Conflict of fileds {0} '.format(
                    set(fields.keys()) - (set(fields.keys()) - 
                                          set(self.item.keys())))) 
            fields.update(self.item)
            #nitemtype = type(itemname, (Item,), fields)
            return fields
        
    def _loader_context(self, context_str):
        try:
            keys = []
            content_dic = ast.literal_eval("{" + context_str.strip(',\t\n ') + "}")
            for k in content_dic.keys():
                keys.append((k, context_str.find(k)))
            keys = sorted(keys, key=lambda x:x[1])
            return ([x[0] for x in keys], dict(content_dic))
        except (SyntaxError,ValueError), e:
            self.logger.log(log.ERROR, "Wrong context definition format: {0} with error {1}".format(context_str, e))
            raise e

            
    def _get_processors(self, procs_str):
        if hasattr(processors, procs_str):
            return getattr(processors, procs_str)
        else:
            self.logger.log(log.ERROR, "Processor '%s' is not defined!" % procs_str)
        
    def _singleelem_parse(self, etreenode, path, regex=None, process=None):
        def process_decorater(p, v, *args):
            if isinstance(v, (list, tuple)) and \
                p not in ('first','join','last', 'alle'):
                return [self._get_processors(p)(_v, *args) for _v in v]
            else:
                return self._get_processors(p)(v, *args)
                    
        if process:
            processes, process_dic = self._loader_context(process)
            if 'static' in process_dic:
                return process_dic['static']
            else:
                if not path:
                    raise ValueError('Wrong element definition')
                content = etreenode.xpath(path)
                if not content:
                    return None
                if not filter(lambda x:x, [processes[0]==x for x in ('first','join','last', 'alle')]):
                    processes.insert(0, 'first')
                    process_dic['first'] = None
                    
                for p in processes:
                    try:
                        if isinstance(process_dic[p], (str, unicode, type(None), )):
                            #content = self._get_processors(p)(content, process_dic[p])
                            content = process_decorater(p, content, process_dic[p])
                        else:
                            #content = self._get_processors(p)(content, process_dic[p])
                            content = process_decorater(p, content, *process_dic[p])
                    except ValueError, e:
                        self.logger.log(log.ERROR, "Process {0} with value {1} error".format(p, [content, process_dic[p]]))
                        raise e
                return content
        else:
            content = etreenode.xpath(path)
            if content:
                content = processors.first(content)
                try:
                    content = str(content)
                except UnicodeEncodeError:
                    content = unicode(content)
            else:
                content = None
                
            return content
        
    def _elems_parse(self, etreenode, fields=[], elemcont={}):
        res = {}
        for f in fields:
            if isinstance(elemcont[f], dict):
                res[f] = self._parser(etreenode, elemcont[f]) 
            else:
                res[f] = self._singleelem_parse(etreenode, *elemcont[f])
        return res
    
    def _parser(self, content, elems):
        """
        从文档树中提取内容

        @param content: 文档树
        @return: an iterator object and element with format (nexturl, item).
            nexturl can be None, an str or iterator object(e.g. list)
        """
        res = []
        if 'base' in elems.keys():
            fields = elems.keys()
            fields.remove('base')
            basetree = content.xpath(elems['base'])
            if basetree:
                for cnode in basetree:
                    res.append(self._elems_parse(cnode,fields, elems))
        else:
            res.append(self._elems_parse(content, elems.keys(), elems))
        return res

    def process(self):
        """
        单个节点或爬虫的测试，这个方法可以查看单个爬虫定义是否正确，即验证elems定义是否正确
        """
        content = html.fromstring(self.download())
        return self._parser(content, self.elems)
    
    
class SpiderNode(AtomicSpiderBase):
    """
    爬虫处理pipeline. 职责: 负责不同爬虫之间的数据链接
    
    Attribute: 
        nextnodes = [(<node>, <urls>, <isdata>),...]
            node: ProcessNode子类. 下一个处理的节点
            urls:(<xpath>, <regex>, <process>).传给下一个处理节点的url, 如果是相对xpath路径，则沿用`elems`元素中的`base`定义的元素
            isdata: True/False, 是否需要当前节点处理的数据
    """
    nextnodes = []

    def __init__(self, url, item=None, ):
        super(SpiderNode, self).__init__(url, item)
        
                
    def spider_name(self, spider):
        if inspect.isclass(spider) and issubclass(spider, SpiderNode):
            return '.'.join((spider.__module__, spider.__name__))
        else:
            return spider
    
    def _reset_elems_with_nexturls(self):
        """  为``elems``添加链接下一些节点的url规则
        """
        def base_dic(dicv):
            if 'base' in dicv:
                return dicv
            else:
                for v in dicv.itervalues():
                    if isinstance(v, dict):
                        return base_dic(v)
                    
        if self.nextnodes:
            nexturls = [('{0}_NEXTURL'.format(e[0] if isinstance(e[0], (str,unicode,)) 
                            else self.spider_name(e[0])), e[1]) 
                            for e in self.nextnodes]
            
            rel_nexturls, abs_nexturls = [], []
            [abs_nexturls.append(x) if x[1][0].startswith('//') else rel_nexturls.append(x) for x in nexturls]
            
            tempelems = self.elems.copy()
            tempelems_with_base = base_dic(tempelems)
            if not tempelems_with_base and rel_nexturls:
                raise ValueError('Nodes {0} connect url is defined with \
                    relative path but ``base`` not define'.format([x[2] for x in rel_nexturls]))
            else:
                tempelems.update(abs_nexturls)
                if tempelems_with_base:
                    tempelems_with_base.update(rel_nexturls)
                return tempelems
        else:
            return self.elems
                
    def _resolve_nexturls(self, dictv):
        """
        从字典值中提取出为链接节点(nodes)的url
        """
        node_urlnexts = {}
        def list_resolve(iterv):
            for e in iterv:
                if isinstance(e, (list,tuple)):
                    list_resolve(e)
                elif isinstance(e, dict):
                    url_resolve(e)
                    
        def url_resolve(dicv):
            kpop = []
            for k, v in dicv.iteritems():
                if isinstance(v, dict):
                    url_resolve(v)
                elif isinstance(v, (list,tuple)) and filter(lambda x:isinstance(x, dict), v):
                    list_resolve(v)
                else:
                    if k.endswith('NEXTURL'):
                        ndname = k[:-len('_NEXTURL')]
                        _v =  v if isinstance(v, (list,tuple)) else [v, ] 
                        if node_urlnexts.get(ndname, None):
                            node_urlnexts[ndname] += _v
                        else:
                            node_urlnexts[ndname] = _v
                        kpop.append(k)
            for k in kpop:
                dicv.pop(k)
                
        url_resolve(dictv)
        return node_urlnexts
    
    def parser(self, content):
        """
        从文档树中提取内容

        @param content: 文档树
        @return: an iterator object and element with format (item, {node1:[urls], node2:[urls],...]).
            nexturl can be None, an str or iterator object(e.g. list)
        """
        elems = self._reset_elems_with_nexturls()
        for x in self._parser(content, elems):
            item = self.get_item()
            if self.nextnodes:
                nodes_nexturls = self._resolve_nexturls(x)
                item.update(x)
                yield (item, nodes_nexturls)
            else:
                item.update(x)
                yield (item, {})
                
    def item_save(self, item):
        """
        save item
        """
        def save(saveset):
            if isclass(saveset['driver']):
                dbdriver = saveset['driver']
            else:
                dbdriver = import_class(saveset['driver'])
            
            if dbdriver:
                dbhandle = dbdriver(**saveset.get('param', {}))
                if saveset.get('alias', {}):
                    value = dict(item)
                    for name, aliasname in saveset['alias'].iteritems():
                        if not value.get(name, None):
                            self.logger.log(log.WARNING, '')
                        else:
                            value[aliasname] = value.pop(name)
                            dbhandle.save(value)
                else:
                    dbhandle.save(dict(item))
                    
        saveset = getattr(self,'save',{})
        if not saveset:
            return
        
        #dbdriver = save_driver(saveset.get('driver',''))
        if isinstance(saveset, (list, tuple)):
            for sconf in saveset:
                save(sconf)
        else:
            save(saveset)
                
    def next_spider(self, spider):
        """
        if the spider ${name} need item data 
        @return True/False
        """
        for spidercls, urls, isdata in self.nextnodes:
            if self.spider_name(spider) == self.spider_name(spidercls):
                if isinstance(spidercls, (str, unicode,)):
                    if '.' in spidercls:
                        modulestr, classtr = spidercls.rsplit('.', 1)
                    else:
                        modulestr, classtr = self.__class__.__module__, spidercls
                    spidercls = getattr(__import__(modulestr),classtr)
                return spidercls, urls, isdata
            
        raise ValueError("The spider of {0} not in nextnodes of spidernode {1}".format(
                        self.spider_name(spider), self.__class__.__name__))

    def pipeline_process(self):
        """
        运行整个爬虫处理流
        """
        content = html.fromstring(self.download())
        for item, nodes_nexturls in self.parser(content):
             
            # save item if save node setted
            self.item_save(item)
                     
            for node, nexturls in nodes_nexturls.iteritems():
                    spidercls, _, isdata = self.next_spider(node)
      
                    # log spider info
                    self.logger.log(log.INFO, 'Next spider: {0}'.format(spidercls.__name__))
                    nurls = [nexturls,] if isinstance(nexturls, (str, type(None))) else nexturls
      
                    # log info
                    self.logger.log(log.INFO, 'Next urls: {0}'.format(nurls))
                      
                    nitem = None if not isdata else item
                    for nurl in nurls:
                        if nurl:
                            spiderobj = spidercls(nurl, nitem)
                            spiderobj.pipeline_process()
                        else:
                            self.logger.log(log.INFO, 
                                "Null url for spider {0} directed by url {1} of spider {2}".format(spidercls.__name__, 
                                                                                                   self.url, 
                                                                                                   self.__class__.__name__, ))

class AsyncSpiderProcess:
    """
    异步方式处理爬虫pipeline. 职责: 负责不同爬虫之间的数据通信
    """
    queue = None
    spiders = {}
    
    # start urls of spier flows and elements with format (spidername, url) 
    start_urls = []
    
    logger = log.getLogger('spiderprocess')
    def __init__(self, queue, start_urls=[]):
        self.queue = queue
        self.start_urls = start_urls
        self.init_process()
        
    def init_process(self):
        for s, url in self.start_urls:
            self.queue.put(url, prespider=None, nextspider=s, item=None)
        pass
    
    def start(self):
        """
        运行整个爬虫处理流
        """
        def get_spider_class(name):
            if '.' in name:
                modulestr, classtr = name.rsplit('.', 1)
            else:
                modulestr, classtr = self.__class__.__module__, name
            spidercls = getattr(__import__(modulestr),classtr)
            
            if not issubclass(spidercls, SpiderNode):
                raise TypeError('{0} is not subclass of \
                        ProcessNode'.format(spidercls))
                
            return spidercls
        
        while(len(self.queue)):
            url, _ps, s, item = self.queue.poll()
            if s in self.spiders:
                spd = self.spiders[s]
                spd.url = url
                if item:
                    spd.item.update(item)
            else:
                spd = s(url, item) if isclass(s) else get_spider_class(s)(url, item)
                self.spiders[s] = spd
                
            # down load page
            try:
                repcont = spd.download()
            except DownloadError:
                self.queue.put(url, _ps, s, item)
                self.logger.log(log.INFO, 'Exception raised when download url {0} and was reinstered to queue'.format(url))
                continue
                
            content = html.fromstring(repcont)
            for item, nodes_nexturls in spd.parser(content):
                spd.item_save(item)
                
                # insert next spider to queue 
                for node, nexturls in nodes_nexturls.iteritems():
                        nurls = [nexturls,] if isinstance(nexturls, (str, type(None))) else nexturls
                         
                        nitem = None if not spd.next_spider(node)[2] else item
                        
                        for nurl in nurls:
                            if nurl:
                                self.queue.put(nurl, spd.__class__.__name__, node, nitem)
                            else:
                                self.logger.log(log.INFO,"Null url for spider {0} directed by url {1} of spider {2}".format(
                                                    node, spd.url, spd.__class__.__name__, ))
