# -*- encoding:utf-8 -*-
from pymongo import MongoClient
from flask import request, Blueprint

from spiderflow import SpiderNode

class MGBlueprint(Blueprint):
    
    def register(self, app, options, first_registration=False):
        Blueprint.register(self, app, options, first_registration=first_registration)
        self.mgclient = MongoClient(options['mongo_host'], options['mongo_port'])

mongo_storage = MGBlueprint('mongo_storage', __name__,)

def get_spiderflow(workspace, nodename):
    """
    根据爬虫处理流的定义创建各个爬虫类实例
    
    @param workspace: 爬虫工作流所在的工作空间
    @param nodename: 工作流的起始爬虫节点名称
    """
    spdflow = {}
    ndcol = mongo_storage.mgclient[workspace]['nodes']
    nddef = ndcol.find_one({'name':nodename}, {'_id':0, 'elems':1, 'save':1, 'nextnodes':1})
    print nddef
    if isinstance(nodename, unicode):
        nodename = nodename.encode('utf-8')
    spdcls = type(nodename, (SpiderNode, ), nddef)
    spdflow[nodename] = spdcls
    if hasattr(spdcls, 'nextnodes'):
        for nddef in spdcls.nextnodes:
            if nddef[0] not in spdflow:
                spdflow.update(get_spiderflow(workspace, nddef[0]))
            spdcls.nextnodes.append([spdflow[nddef[0]],]+ nddef[1:])
            spdcls.nextnodes.remove(nddef)
    return spdflow

@mongo_storage.route('/newspiderflow/<workspace>/', methods=['POST', ])
def newspiderflow(workspace=None):
    """
    创建新的爬虫工作流空间
    
    @return:
    """
    if request.method == 'POST':
        config_col = mongo_storage.mgclient[workspace]['conf']
        config_col.insert({'currentDate':{'createTime':True}})
        return 'Success'

@mongo_storage.route('/delspiderflow/<workspace>/', methods=['POST', ])
def delspiderflow(workspace):
    """
    删除一个爬虫工作流
    
    @return: 
    """
    if request.method == 'POST':
        mongo_storage.mgclient.drop_database(workspace)
        return 'Success'

@mongo_storage.route('/spiderflowexec/<workspace>/', methods=['POST',])
def spiderflowexec(workspace):
    """
    执行某工作空间内的爬虫工作流. 执行前先检测保存，再执行.
    
    @return:
    """
    # save defination to db
    if request.method == 'POST':
        if request.args.get('url', ''):
            for node in request.json:
                ndcol = mongo_storage.mgclient[workspace]['nodes']
                ndcol.update({'name':node['name']}, node, upsert=True)
                
            config_col = mongo_storage.mgclient[workspace]['conf']
            config_col.insert({'default_startnode':request.json[0]['name']})
                
            startnode_name = request.json[0]['name']
            spdflow = get_spiderflow(workspace, startnode_name)
            
                        # 开始执行
            spdflow[startnode_name](request.args['url']).pipeline_process()
            
            return 'Success'
        else:
            return u"缺少url参数", 403
        
@mongo_storage.route('/spiderflowattrs/<workspace>/', 
                methods=['GET', 'PUT',])
def spiderflowattrs():
    """
    获取或修改某一爬虫工作流属性信息
    """
    return ''

