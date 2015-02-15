from exceptions import NotImplementedError
from spiderflow import log

class StorageBase:
    logger = log.getLogger('storage')
    
    def save(self, value):
        raise NotImplementedError()