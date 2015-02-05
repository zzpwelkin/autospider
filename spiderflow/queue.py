#-*- encoding:UTF8 -*-
"""
url check queue 
"""
class SpiderQueue:
    __spiders = []
    def put(self, url, prespider, nextspider, item):
        self.__spiders.append((url, prespider, nextspider, item))
    
    def poll(self):
        try:
            return self.__spiders.pop(0)
        except IndexError:
            return None
        
    def __len__(self):
        return len(self.__spiders)