import os
import pickle

CACHE_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data_cache')


class Cache:
    """
    Loads information from and dumps to a cache pickel file.
    """

    def __init__(self, name: str = 'default') -> None:
        '''Creates Cache instance'''
        if not os.path.exists(CACHE_FOLDER):
            os.makedirs(CACHE_FOLDER)

        self.filename = os.path.join(CACHE_FOLDER, f'{name}_cache.pkl')
        self.load_cache()

    def __repr__(self) -> str:
        '''Returns cache contents to print'''
        result = ''
        for k, v in self._data.items():
            result += f'{k} = {v}\n'
        return result

    def __getitem__(self, key: str) -> list:
        '''Return value if key in the cache'''
        return self._data.get(key, [])

    def __setitem__(self, key: str, value: []) -> None:
        '''Set key/value pair'''
        self._data[key] = value
        self.dump()

    def load_cache(self) -> None:
        '''Loads cache if it exists'''
        try:
            with open(self.filename, 'rb') as cache:
                self._data = pickle.load(cache)
        except FileNotFoundError:
            self._data = {}

    def dump(self) -> None:
        '''Dumps the cache dictionary back into the cache file'''
        try:
            with open(self.filename, "wb") as file:
                pickle.dump(self._data, file)
        except Exception as e:
            print(f'Error writing to cache: {e}')

    def flush(self) -> None:
        '''Empties cache'''
        self._data = {}
        self.dump()

    @property
    def cache_data(self):
        self.load_cache
        return self._data