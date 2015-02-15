from sqlalchemy import create_engine, MetaData
from . import StorageBase

class RDBStorage(StorageBase):
    
    def __init__(self, host='localhost', port=3306, username='', 
                    password='', database='', charset='utf8', verbose=False, **kwargs):
        self.engine = create_engine("mysql://{u}:{p}@{h}:{prt}/{db}".format(
                        u=username, p=password, h=host, prt=port, db=database),
                        encoding=charset, echo=verbose)
        self.metadata = MetaData()
        self.metadata.reflect(self.engine, views=True,)
        self.kwargs = kwargs
        