from sqlalchemy import create_engine, MetaData
from . import StorageBase

class RDBStorage(StorageBase):
    
    def __init__(self, host='localhost', port=3306, username='', 
                    password='', database='', charset='utf8', verbose=False, driver='mysql', **kwargs):
        
        if driver=='mysql':
            # Note: 
            self.engine = create_engine("{dr}://{u}:{p}@{h}:{prt}/{db}?charset={cs}&use_unicode=0".format(
                            dr=driver,u=username, p=password, h=host, prt=port, db=database, 
                            cs=charset),encoding=charset, echo=verbose)
        else:
            self.engine = create_engine("{dr}://{u}:{p}@{h}:{prt}/{db}".format(
                            dr=driver,u=username, p=password, h=host, prt=port,
                            db=database,),encoding=charset, echo=verbose)
        self.metadata = MetaData()
        self.metadata.reflect(self.engine, views=True,)
        self.kwargs = kwargs
        
class SqlalchemyStoragy(StorageBase):
    def __init__(self, engine, tables = {}):
        self._engine = engine
        self._tables = tables
        
    def get_table(self, name):
        """
        get Table instance by name
        """
        tb = self._tables.get(name, None)
#         if tb is not None and tb.bind is None:
#             if self._engine is None:
#                 raise Exception(u"Table {0} cat't be bind to any engine".format(name))
#             tb.bind = self._engine   
        return tb
        