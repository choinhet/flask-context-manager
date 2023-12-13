class KeyUtility:
    @classmethod
    def auto_set_key(cls, clz):
        annotations = clz.__annotations__
        for name, annotation in annotations.items():
            setattr(clz, name, name)
        return clz
