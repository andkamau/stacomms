"""
Usage:
======

>>> from commonutils.memcache.core import MemcacheHandler
>>> memcache = MemcacheHandler()
>>> memcache.set('my_key', 'my_value')
>>> memcache.get('my_key')
>>> memcache.delete('my_key')
>>> memcache.flush_all()
"""


from commonutils.common.core import log
from commonutils.memcache.config import MEMCACHE


try:
    import memcache
except ImportError:
    log('!! Memcache Python Client not installed !!', 'error')
    raise ImportError

class MemcacheHandler:
    def __init__(self, ):
        self.memc_client = memcache.Client(
                [MEMCACHE['host']], debug=1, socket_timeout=3)

    
    def set(self, key, value,
        retention_period=int(MEMCACHE['retention_period'])):
        memc = self.memc_client
        memc_set = memc.set( key, value, time=int(retention_period) )
        if str(memc_set) != '0':
            log('MEMCACHE: Set -- %s -- %s -- %s' % (key, value, 
                str(retention_period)), 'info')
        else:
            log('MEMCACHE: Error: failed to set. %s' % (memc_set), 'info')
    
    
    def get(self, key):
        memc = self.memc_client
        return memc.get(key)


    def delete(self, key):
        memc = self.memc_client
        if memc.delete(key) != 0:
            # Nonzero on success.
            log(' MEMCACHE: Successfully deleted %s' % str(key))
        else:
            log(' MEMCACHE: Could not delete %s' % str(key))


    def flush_all(self):
        memc = self.memc_client
        memc.flush_all()
        log(' MEMCACHE: All data expired' )
