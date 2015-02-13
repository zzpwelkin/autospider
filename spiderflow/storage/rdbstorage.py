from spiderflow import log
from sqlalchemy import create_engine, MetaData

class CarDbDriver:
    logger = log.getLogger('storage')
    
    def __init__(self, host='localhost', port=3306, username='', 
                    password='', database='', charset='utf8', **kwargs):
        self.engine = create_engine("mysql://{u}:{p}@{h}:{prt}/{db}".format(
                        u=username, p=password, h=host, prt=port, db=database),
                        encoding=charset, echo=True)
        self.metadata = MetaData()
        self.metadata.reflect(self.engine, database, views=True,)
        self.kwargs = kwargs
        
    def save(self, value):
        self.engine.execute(
                        self.metadata.tables[''].ins(value.keys()).values(value.values())
                        )
        
