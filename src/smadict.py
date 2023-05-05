import time
from collections.abc import MutableMapping
from threading import Lock

class SMA_Dict(MutableMapping):
    """
    A thread-safe dictionary with callbacks.

    Allows multiple threads to access and modify the dictionary concurrently,
    while ensuring that the dictionary is always in a consistent state.

    Whenever an item is updated in the dictionary, all registered callbacks are
    called with the updated key-value pair.

    Parameters:
    -----------
    *args, **kwargs : optional
        Any key-value pairs to initialize the dictionary with.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the SMA_Dict instance.

        Creates an empty dictionary, a list of callbacks, and a lock to ensure
        thread safety. Updates the dictionary with any key-value pairs provided
        in *args and **kwargs.

        Parameters:
        -----------
        *args, **kwargs : optional
            Any key-value pairs to initialize the dictionary with.
        """
        self.store = dict()
        self._callbacks = []
        self._lock = Lock()
        self.update(dict(*args, **kwargs))

    def register_callback(self, callback):
        """
        Registers a callback function to be called when a key-value pair is updated.

        Parameters:
        -----------
        callback : callable
            The function to be called. Must accept two parameters: the key that was
            updated, and the new value of the key.
        """
        self._callbacks.append(callback)

    def __getitem__(self, key):
        """
        Retrieves the value associated with the given key.

        Parameters:
        -----------
        key : hashable
            The key whose value should be retrieved.

        Returns:
        --------
        value : any
            The value associated with the given key.

        Raises:
        -------
        KeyError:
            If the given key is not found in the dictionary.
        """
        with self._lock:
            return self.store[key]

    def __setitem__(self, key, value):
        """
        Updates the value associated with the given key, and calls any registered callbacks.

        Parameters:
        -----------
        key : hashable
            The key whose value should be updated.
        value : any
            The new value to associate with the given key.
        """
        with self._lock:
            self.store[key] = value

            for callback in self._callbacks:
                callback(key, value)

    def __delitem__(self, key):
        """
        Removes the key-value pair associated with the given key.

        Parameters:
        -----------
        key : hashable
            The key whose key-value pair should be removed.

        Raises:
        -------
        KeyError:
            If the given key is not found in the dictionary.
        """
        with self._lock:
            del self.store[key]

    def __iter__(self):
        """
        Returns an iterator over the keys in the dictionary.

        Returns:
        --------
        iterator : iterator
            An iterator over the keys in the dictionary.
        """
        with self._lock:
            return iter(self.store)

    def __len__(self):
        """
        Returns the number of key-value pairs in the dictionary.

        Returns:
        --------
        length : int
            The number of key-value pairs in the dictionary.
        """
        with self._lock:
            return len(self.store)

    def __copy__(self):
        """
        Return a shallow copy of the SMA_Dict object.

        Returns:
        --------
            SMA_Dict: A new SMA_Dict object with the same key-value pairs as the original object.
        """ 
        new_dict = SMA_Dict()
        new_dict.store = self.store.copy()
        return new_dict