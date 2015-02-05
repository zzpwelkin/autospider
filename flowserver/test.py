#-*- encoding:UTF8 -*-

import os
import sys
# import tempfile
from unittest import main as testmain
from unittest import TestCase

from flask import json

sys.path.append(os.path.dirname(__name__))
from server import app

print app.root_path

# setup the TESTING config flag is activated. What it does is 
# disabling the error catching during request handling 
app.config['TESTING'] = True

# 设置测试的爬虫服务目录
# app.config['SPIDERFLOWSDIR'] = tempfile.mkdtemp('spiderflow', 
#                 dir='/tmp')

c = app.test_client()

class FlowTest(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        
    def tearDown(self):
        TestCase.tearDown(self)
        
    def test_newspiderflow_and_delspiderflow(self):
        pass
        
    def test_processes(self):
        """
        processes 列表测试
        """
        resp = c.get('/processes/')
        self.assertDictContainsSubset({'join':None, 'alle':None}, 
                        json.loads(resp.data,))
        
    def test_spiderprocess(self):
        """
        单一spider处理测试
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
        ressubdic = {'name': u'布加迪',
                        'url': 'http://car.autohome.com.cn/price/brand-37.html',
                        'subbrands': [{'models': [
                                        {'name': u'威航','url': 'http://www.autohome.com.cn/390/'},
                                        {'name': 'Galibier','url': 'http://www.autohome.com.cn/920/'}
                                        ],'name': u'布加迪'}],
                                                     }
        
        resp = c.post('/spiderexec/Autohome/?url=http://www.autohome.com.cn/grade/carhtml/B.html',
                        data = json.dumps(elems), content_type='application/json')
        self.assert_(200 == resp.status_code, 
                        '{0} status code is returned and response body is {1}'.format(resp.status_code, resp.data))
        self.assert_(filter(lambda url: url==ressubdic['url'], [x['url'] for x in json.loads(resp.data,)]))
        
    def test_pipeline(self):
        """
        爬虫工作流测试
        """
        spdflow = [{'name':'Brand', 
                        'elems':{
                                        'base':'//ul[contains(@class,"list")]/li/a[2]',
                                        'url':('@href', None, None),
                                        'name':('text()', None, None)
                                                    }, 
    'nextnodes':[('Series', ('@href', None, None), True), ]},
    {'name':'Series',
        'elems':{
             'models':{
                       'base':'//div[contains(@id,"MasterSerialList_0")]/ul/li/div[@class="title"]/a',
                       'url':('@href', None, '"pre_url":"http://car.bitauto.com"'),
                       'name':('text()', None, None),
                            }
             },
    'save':{'driver':'mongodb', 'param':{'db':'a', 'collection':'models'}, 'alias':{'url':'_id'}},
    }
    ]
        c.post('/newspiderflow/bitauto/')
        resp = c.post('/spiderflowexec/bitauto/?url=http://car.bitauto.com/qichepinpai/',
              data = json.dumps(spdflow), content_type='application/json')
        self.assert_(200 == resp.status_code, 
                    '{0} status code is returned and response body is {1}'.format(resp.status_code, resp.data))
    
if __name__ == "__main__":
    testmain()
#     suite = TestSuite()
#     t = TestLoader()
#     suite.addTest(t.loadTestsFromTestCase(FlowTest))
#     TextTestRunner().run(suite)