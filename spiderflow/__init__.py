import logging as log

def default_logger():
    defhandle = log.StreamHandler()
    loger = log.Logger('myspider')
    loger.handlers.append(defhandle)
    return loger

def save_driver(db):
    from .storage import MongoDBDriver
    driver = {'mongodb':MongoDBDriver, }
    return driver.get(db, None)

def urls_check_queue():
    pass

from .item import Field, Item
from .spider import ProcessNode

__all__ = ['Field', 'Item', 'ProcessNode','log', 'default_logger', 'save_driver']