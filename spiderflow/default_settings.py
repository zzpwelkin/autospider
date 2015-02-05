#-*- encoding:utf8 -*-

"""
default settings
"""
LOGGER = {
                'version':1,
                'handlers':
                {
                                'console':
                                {
                                                'class':'logging.StreamHandler', 
                                                 'level'   : 'INFO',
                                                 'stream'  : 'ext://sys.stdout'
                                                }
                                },
                                'loggers':
                                {
                                                'spider':
                                                {
                                                                'handlers':['console',],
                                                                'propagate':True,
                                                                'level':'INFO',
                                                                },
                                                 'spiderprocess':
                                                {
                                                                'handlers':['console',],
                                                                'propagate':True,
                                                                'level':'INFO',
                                                                },
                                                 'process':
                                                {
                                                                'handlers':['console',],
                                                                'propagate':True,
                                                                'level':'INFO',
                                                                },
                                                 'storage':
                                                {
                                                                'handlers':['console',],
                                                                'propagate':True,
                                                                'level':'INFO',
                                                                },
                                                },
                }