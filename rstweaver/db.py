
import shelve
import atexit
import os
from utils import makepdir
from collections import deque, namedtuple

def make_db(db_path):
    makepdir(os.path.dirname(db_path))
    base = shelve.open(db_path)
    handle = DictProxy(base)
    
    atexit.register(handle.close)
    
    return handle

class DictProxy(object):
    '''
    This isn't actually about caching but about keeping identity.
    '''
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

class ActionCache(object):
    
    def __init__(self, size=100):
        self.time_list = deque([None] * size)
        self.actions = { }
    
    def __setitem__(self, key, value):
        value_set = self.actions.get(key, set())
        
        if value not in value_set:
            self.push(key, value)
        
        value_set.add(value)
        self.actions[key] = value_set
    
    def __getitem__(self, key):
        return self.actions.get(key, set())
    
    def push(self, new_key, new_value):
        left = self.time_list.popleft()
        if left != None:
            (last_key, last_value) = left
            
            value_set = self.actions.get(last_key, set())
            value_set.remove(last_value)
            
            if len(value_set) == 0:
                del self.actions[last_key]
            
        self.time_list.append((new_key, new_value))

class Action(object):
    
    def __init__(self, inputs, outputs, output):
        self.inputs  = tuple(inputs)
        self.outputs = outputs
        self.output  = output
        
        self._action = self.inputs
    
    def __hash__(self):
        return hash(self._action)
    
    def __cmp__(self, other):
        return cmp(self._action, other._action)
    
    def __str__(self):
        return '%s --> %s' % (self.inputs, self.outputs)
    
    def __repr__(self):
        return self.__str__()


