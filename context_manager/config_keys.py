def auto_set_key(cls):
    annotations = cls.__annotations__
    for name, annotation in annotations.items():
        setattr(cls, name, name)
    return cls


@auto_set_key
class Contained:
    CONTROLLERS: str
    CONFIGURATIONS: str
    SERVICES: str
    COMPONENTS: str
    REPOSITORIES: str


@auto_set_key
class BaseKey:
    FOLDERS: str
