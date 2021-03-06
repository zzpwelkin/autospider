from exceptions import NotImplementedError
from spiderflow import log

class StorageBase(object):
    logger = log.getLogger('storage')
    
    def save(self, value):
        raise NotImplementedError()