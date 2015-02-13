#!/usr/bin/env python
#-*- encoding:utf8 -*-
import codecs

class ConsoleStream:

    def _print(self, value):
        print u' '.join([u':'.join(x if x[1] else (x[0], '')) for x in value.iteritems()])
        
    def save(self, value):
        self._print(value)
        
class FileStream:
    """
    fw: an object of file
    write: write method
    """
    def __init__(self, f, append=False, format='text', encoding='utf8'):
        """
        file mimetype, can be text or csv
        """
        wmode = 'w' if not append else 'a'
        if format == 'csv':
            import csv
            self.fw = csv.writer(open(f, wmode))
            self.write = lambda v: self.fw.writerow([x.encode(encoding) if x else '' for x in v])
        else:
            writer = codecs.getwriter(encoding)
            self.fw = writer(open(f, wmode) )
            self.write = lambda v: self.fw.write(u' '.join(v)+'\n')
        
    def save(self, value):
        self.write(value.values())
