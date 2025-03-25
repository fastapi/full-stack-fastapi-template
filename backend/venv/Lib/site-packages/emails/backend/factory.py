# encoding: utf-8

def simple_dict2str(d):
    # Simple dict serializer
    return ";".join(["%s=%s" % (k, v) for (k, v) in d.items()])

_serializer = simple_dict2str

class ObjectFactory:

    """
    Get object from cache or create new object.
    """

    def __init__(self, cls):
        self.cls = cls
        self.pool = {}

    def __getitem__(self, k):
        if not isinstance(k, dict):
            raise ValueError("item must be dict, not %s" % type(k))
        cache_key = _serializer(k)
        obj = self.pool.get(cache_key, None)
        if obj is None:
            obj = self.cls(**k)
            self.pool[cache_key] = obj
        return obj

    def invalidate(self, k):
        cache_key = _serializer(k)
        if cache_key in self.pool:
            del self.pool[cache_key]
        return self[k]