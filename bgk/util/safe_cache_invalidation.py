from functools import cached_property

__all__ = ["safe_cached_property_invalidation"]


def safe_cached_property_invalidation(cls):
    # type annotations break vscode's intellisense for some reason, so don't add them to the function signature

    cls._CACHED_ATTRS = [k for k, v in cls.__dict__.items() if isinstance(v, cached_property)]

    def safe_delete(self: cls, name: str):
        if hasattr(self, name):
            super(cls, self).__delattr__(name)
        elif name in cls._CACHED_ATTRS:
            return
        else:
            raise AttributeError(obj=self, name=name)

    cls.__delattr__ = safe_delete
    return cls
