import datetime
import re
from lxml import html, etree

from spiderflow import log

logger = log.getLogger('process')

_elem_str = lambda elem, encoding: html.tostring(elem) \
        if isinstance(elem, etree.ElementBase) else elem 

# elements select processes
first = lambda elems, encoding='utf-8': _elem_str(elems[0], encoding)
last = lambda elems, encoding='utf-8': _elem_str(elems[-1], encoding)
alle = lambda elems, encoding='utf-8': [_elem_str(e, encoding) for e in elems]
def join(elems, s, encoding='utf-8'):
    res = [_elem_str(e, encoding) for e in elems]
    return s.join(res)

# string processes
str_replace = lambda text, olds, news, count=None: text.replace(olds, news, count) \
                if count else text.replace(olds, news)
pre_str = lambda text, s: s + text
post_str = lambda text, s: text + s
none_to_str = lambda text, default: default if text is None else text

def str_strip(text, s):
    """
    string strip method
    """
    return text.strip(s)

def re_str(text, s):
    res = re.findall(s, text, )
    return res[0] if res else ''

def pre_url(text, s):
    pre_url = s
    if(pre_url[0:7] == 'http://' and text[0:7] == 'http://'):
        return text
    
    if(pre_url[-1:] == '/' and text[0:1] == '/'):
        pre_url = pre_url[:-1]
    
    return pre_url + text

# page evaluate process
def eva_pages(text, pattern, start, step=1):
    """
    text: last page url
    pattern:
    """
    res = []
    pre_str, lastpage, post_str = re.split(pattern.replace('{page}', '(\d+)'), text)
    if lastpage.isdigit():
        for i in xrange(start,int(lastpage)+1,step):
            res.append(''.join((pre_str, pattern.format(page=i), post_str)))
        return res
    else:
        logger.log(log.WARN, u'Page number {0} with pattern {1} from {2} is not a number and source text was returned'.format(lastpage, pattern, text))
        return text

# def date(text, loader_context):
#     cformat = loader_context.get('date')
#     try:
#         if text.lower() in ['gestern', 'yesterday',]:
#             date = datetime.date.today() - datetime.timedelta(1)
#         elif text.lower() in ['heute', 'today',]:
#             date = datetime.date.today()
#         elif text.lower() in ['morgen', 'tomorrow',]:
#             date = datetime.date.today() + datetime.timedelta(1)
#         else:
#             date = datetime.datetime.strptime(text, cformat)
#     except ValueError:
#         loader_context.get('spider').log('Date could not be parsed ("%s", Format string: "%s")!' % (text, cformat), log.ERROR)
#         return None
#     return date.strftime('%Y-%m-%d')


# def time(text, loader_context):
#     cformat = loader_context.get('time')
#     try:
#         time = datetime.datetime.strptime(text, cformat)
#     except ValueError:
#         loader_context.get('spider').log('Time could not be parsed ("%s", Format string: "%s")!' % (text, cformat), log.ERROR)
#         return None
#     return time.strftime('%H:%M:%S')
# 
# 
# def _breakdown_time_unit_overlap(time_str, limit):
#     time_list = time_str.split(':')
#     first = int(time_list[0])
#     if first >= limit:
#         time_list[0] = str(first % limit)
#         time_list.insert(0, str(first // limit))
#     else:
#         if(len(time_list[0]) == 1):
#             time_list[0] = '0' + time_list[0]
#         time_list.insert(0, '00')
#     time_str = ':'.join(time_list)
#     return time_str
# 
# 
# def duration(text, loader_context):
#     cformat = loader_context.get('duration')
#     #Value completion in special cases
#     text_int = None
#     try:
#         text_int = int(text)
#     except ValueError:
#         pass
#     if(cformat == '%H:%M'):
#         if text_int:
#             text += ':00'
#     if(cformat == '%M'):
#         text = _breakdown_time_unit_overlap(text, 60)
#         cformat = '%H:%M'
#     if(cformat == '%M:%S'):
#         if text_int:
#             text += ':00'
#         text = _breakdown_time_unit_overlap(text, 60)
#         cformat = '%H:%M:%S'
#     if(cformat == '%S'):
#         text = _breakdown_time_unit_overlap(text, 60)
#         cformat = '%M:%S'
#     try:
#         duration = datetime.datetime.strptime(text, cformat)
#     except ValueError:
#         loader_context.get('spider').log('Duration could not be parsed ("%s", Format string: "%s")!' % (text, cformat), log.ERROR)
#         return None
#     return duration.strftime('%H:%M:%S')
