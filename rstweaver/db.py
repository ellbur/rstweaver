
import shelve
import atexit
import os
from utils import makepdir

db_path = os.path.expanduser('~/.cache/rstweaver/cache')
handle = None
cache_disabled = False

def disable_cache():
    global cache_disabled
    cache_disabled = True

def open_db():
    if cache_disabled:
        return { }
    
    if handle != None:
        return handle
    
    return init_db()
    
def init_db():
    global handle
    
    makepdir(os.path.dirname(db_path))
    base = shelve.open(db_path)
    handle = DictProxy(base)
    
    atexit.register(close_db)
    
    return handle

def close_db():
    if cache_disabled:
        return
    handle.close()

class DictProxy(object):
    
    def __init__(self, dict):
        self.dict  = dict
        self.proxy = { }
    
    def __getitem__(self, key):
        if key not in self.proxy:
            self.proxy[key] = self.dict[key]
            
        return self.proxy[key]
    
    def __setitem__(self, key, value):
        self.proxy[key] = value
        self.dict[key] = value
    
    def __contains__(self, key):
        return (key in self.proxy) or (key in self.dict)
    
    def close(self):
        for key, value in self.proxy.items():
            self.dict[key] = value
        
        self.dict.close()

