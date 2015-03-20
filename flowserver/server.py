#-*- encoding:UTF8 -*-
"""
爬虫工作流的服务器

工作流平台信息用mongodb数据库支持
"""

from flask import Flask, request, json
from bluprints import spider
from spiderflow import SpiderNode

# 定义服务application
app = Flask(__name__)

app.register_blueprint(spider.spider_info)

if app.config.get('STORAGE_DRIVER', 'MONGO'):
    from bluprints import mongo
    app.register_blueprint(mongo.mongo_storage, mongo_host='localhost', mongo_port=27017)

@app.route('/spiderexec/<spidername>/', methods=['POST', ])
def spiderexec(spidername):
    """
    执行一个单一的爬虫
    
    @param elems: 爬取的内容定义
    @param url: 要测试网站的url
    
    @return: 执行结果
    """
    if request.method == 'POST':
        if request.args.get('url', ''):
            res = []
            if isinstance(spidername, unicode):
                spidername = spidername.encode('utf-8')
            spdcls = type(spidername, (SpiderNode, ), 
                    {'elems':request.json})
            
            for x in spdcls(request.args['url']).process():
                res.append(x)

            return app.make_response((json.dumps(res), 200, {'content-type':'application/json'}))
            #return jsonify(res)
        else:
            return u"缺少url参数", 403
    

if __name__ == "__main__":
    app.debug=True
    app.run()