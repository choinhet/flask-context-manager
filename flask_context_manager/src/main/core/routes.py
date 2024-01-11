def rest_mapping(prefix):
    def decorator(cls):
        cls._route_prefix = prefix
        return cls

    return decorator


def get_mapping(route):
    def decorator(f):
        f._route = route
        f._methods = ['GET']
        return f

    return decorator


def post_mapping(route):
    def decorator(f):
        f._route = route
        f._methods = ['POST']
        return f

    return decorator


def put_mapping(route):
    def decorator(f):
        f._route = route
        f._methods = ['PUT']
        return f

    return decorator


def delete_mapping(route):
    def decorator(f):
        f._route = route
        f._methods = ['DELETE']
        return f

    return decorator
