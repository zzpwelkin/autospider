#-*- encoding:UTF8 -*-
import pymongo
#from spiderflow import log
from . import StorageBase

class MongoDBDriver(StorageBase):
    #logger = log.getLogger('storage')
    def __init__(self, host='localhost', port=27017, db='test', collection='collection', **kwargs):
        """
        如果存在名称为_id的字段，则使用此字段中的值为documents的_id

        @param upsert: 当存在名称为_id的字段时，如果该_id存在，
            且upins为True则更新其内容;否则不做更改
            z
        @param kwargs: Others paramters of mongodb, e.g. socketTimeoutMS, connectTimeoutMS

        @return: 文档``_id``
        """
        self._param = kwargs.copy()
        fparam = kwargs.copy()
        if 'upsert' in fparam:
            fparam.pop('upsert')
        self._collect = pymongo.MongoClient(host, port, **fparam)[db][collection]
        
    def save(self, value):
        """
        @param value: 字典类型
        """
        if '_id' in value.keys():
            try:
                self._collect.insert(value)
                self.logger.info('Insert document with _id {0}'.format(value['_id']))
            except pymongo.errors.DuplicateKeyError:
                if self._param.get('upsert',False):
                    v = value
                    _id = v.pop('_id')
                    self._collect.update({'_id':_id}, {'$set':v}, \
                            upsert=True)
                    self.logger.info('Update document of _id {0}'.format(_id))
        else:
            _id = self._collect.insert(dict(value))
            self.logger.info('Insert value with automatic _id:{0}'.format(_id))
