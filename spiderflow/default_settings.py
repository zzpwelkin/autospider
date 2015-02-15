#-*- encoding:utf8 -*-

"""
default settings
"""
LOGGER = {
        'version':1,
        'formatters': {
            'detail':{
                'format':'%(name)s %(levelname)s %(pathname)s %(process)d %(thread)d %(message)s\n',
                'datefmt':'%Y-%m-%d %H:%M:%S',
                },
            'simple':{
                'format':'%(name)s %(levelname)s: %(message)s\n',
                'datefmt':'%Y-%m-%d %H:%M:%S',
                },
            },
        'handlers':
        {
            'console':
            {
                'class':'logging.StreamHandler', 
                'level'   : 'INFO',
                'stream'  : 'ext://sys.stdout',
                'formatter': 'simple', 
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
