#-*- coding:utf-8 -*-
"""
search the data
TODO intergrate sphinx search engine for large data repo
"""
import os
from util import *
import codecs

class SearchEngine:
    def search(self, keyword):
        raise NotImplementedError

class TextSearchEngine(SearchEngine):
    def __init__(self, repo):
        self.repo = repo

    def search(self, keyword):
        """
        walk through the given repo and search text
        """
        result = [] #hold the result
        logger.info("search %s from %s" % (keyword, self.repo))
        for dirpath, dirs, files in os.walk(self.repo):
            if '.hg' in dirs:
                dirs.remove('.hg') #don't visit hg directory
            for fn in files:
                file_path = os.path.join(dirpath, fn)
                #logger.info("open file %s for search" % file_path)
                last_dot = fn.rfind('.')
                if last_dot != -1 and fn[last_dot:] in ['.md','.txt']: #only support md and txt

                    fsock = codecs.open(file_path, mode='r',encoding='utf-8')

                    while True:
                        line = fsock.readline()
                        if line == '': #EOF
                            break
                        if keyword in line or keyword.lower() in line.lower():
                            path = file_path.replace(config.datadir, '') #trim data dir
                            result.append((path, line))
                            break #only get the first matching

                    fsock.close()
        return result


