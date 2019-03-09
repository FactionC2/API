from flask_caching import Cache
cache = Cache(config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': './cache'})