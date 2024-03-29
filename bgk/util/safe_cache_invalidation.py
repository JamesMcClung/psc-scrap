from functools import cached_property

__all__ = ["safe_cached_property_invalidation"]


def safe_cached_property_invalidation(cls):
    # type annotations break vscode's intellisense for some reason, so don't add them to the function signature

    cls._CACHED_ATTRS = [k for k, v in cls.__dict__.items() if isinstance(v, cached_property)]

    # note: don't use hasattr. It calls getattr, which triggers the cached_property to create and cache the attribute.
    def safe_delete(self: cls, name: str):
        try:
            super(cls, self).__delattr__(name)
        except AttributeError as e:
            if name not in cls._CACHED_ATTRS:
                raise e

    cls.__delattr__ = safe_delete
    return cls
