import logging as log

def set_logger(conf=None):
    from logging import config
    if not conf:
        from .default_settings import LOGGER
        config.dictConfig(LOGGER)
    else:
        config.dictConfig(conf)
        
set_logger()

# conf = {}
# 
# def settings(**kwargs):
#     for k, v in kwargs.iteritems(): 
#         if isinstance(v, dict):
#             if not conf.get(k, None):
#                 conf[k] = v
#             else:
#                 conf[k].update(dict)
#         elif isinstance(v, (list, tuple,)):
#             if not conf.get(k, None):
#                 if isinstance(v, tuple) or isinstance(conf[k], tuple):
#                     conf[k] = conf[k] + v
#                 conf[k].append(v)
#             else:
#                 conf[k] = v
#         else:
#             conf[k] = v 

from .item import Field, Item
from .spider import SpiderNode, AsyncSpiderProcess
from .queue import MemoryQueue

__all__ = ['Field', 'Item', 'SpiderNode', 'AsyncSpiderProcess', 'MemoryQueue', 'log']