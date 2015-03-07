"""
BSD store for webpy session
"""
import os
from datetime import datetime, timedelta

from web import session

class MemStore(session.Store):
    """
    implement session store in the memory for small data
    it will provide a extreme fast performance without need to de/encode and IOs
    """
    def __init__(self, dic=None):
        if dic:
            self.db = dic
        else:
            self.db = {}

    def __contains__(self, key):
        return self.db.has_key(key)

    def __getitem__(self, key):
        return self.db[key][1]
    
    def __setitem__(self, key, value):
        now = datetime.now()
        self.db[key] = (now, value)

    def __delitem__(self, key):
        if self.db.has_key(key):
            del self.db[key]

    def cleanup(self, timeout):
        timeout = timedelta(seconds=timeout)
        now = datetime.now()
        for key, value in self.db.items():
            if now - self.db[key][0] > timeout:
                del self.db[key]

class BSDStore(session.Store):
    def __init__(self, root):
        import bsddb
        if hasattr(root, '__setitem__') and hasattr(root, '__setitem__'):
            self.db = root
            return
        if not os.path.isdir(root):
            os.makedirs(root)
        dbenv = bsddb.db.DBEnv()
        dbenv.open(root, bsddb.db.DB_CREATE | bsddb.db.DB_INIT_MPOOL | bsddb.db.DB_THREAD)
        d = bsddb.db.DB(dbenv)
        d.open('sessions.db', bsddb.db.DB_BTREE, bsddb.db.DB_CREATE, 0666)
        self.db = bsddb._DBWithCursor(d)

    def __contains__(self, key):
        return key in self.db

    def __getitem__(self, key):
        try:
            return self.decode(self.db[key])[1] #the second item is the data
        except Exception:
            #shield all the exception to the KeyError
            raise KeyError, key

    def __setitem__(self, key, value):
        now = datetime.now()
        self.db[key] = self.encode((now, value))

    def __delitem__(self, key):
        if key in self.db:
            del self.db[key]

    def cleanup(self, timeout):
        if not hasattr(self.db, 'iteritems'):
            return
        now = datetime.now()
        timeout = timedelta(seconds=timeout)
        for key, value in self.db.iteritems():
            if now - self.decode(value)[0] > timeout:
                del self.db[key]
