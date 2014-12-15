# -*- encoding:utf-8 -*-
import inspect
from flask import request, Blueprint, jsonify
from spiderflow import processors, storage

spider_info = Blueprint('spider_info', __name__)

@spider_info.route('/processes/')
def processes():
    """
    获取当前系统提供的process
    
    @return: 
    """
    res = []
    for prs in inspect.getmembers(processors, inspect.isfunction):
        res.append((prs[0], 
            inspect.getdoc(prs[1]) or inspect.getcomments(prs[1])))
        
    return jsonify(res)

@spider_info.route('/persistdrivers/')
def persistdrivers():
    """
    获取当前系统提供的持久化(persist)驱动
    
    @return: 
    """
    res = []
    for stcls in inspect.getmembers(storage, inspect.isclass):
        res.append((stcls[0], 
            inspect.getdoc(stcls[1]) or inspect.getcomments(stcls[1])))

    return jsonify(res)