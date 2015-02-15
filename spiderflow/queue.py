#-*- encoding:UTF8 -*-
"""
url check queue 
"""
class MemoryQueue(object):
    __spiders = []
    
    def put(self, url, prespider, nextspider, item):
        self.__spiders.append((url, prespider, nextspider, item))
    
    def poll(self):
        try:
            return self.__spiders.pop(0)
        except IndexError:
            return None
        
    def __getstate__(self):
            return self.__spiders
        
    def __setstate__(self, state):
            self.__spiders = state
        
    def __len__(self):
        return len(self.__spiders)