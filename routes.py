from app import app


def get_mapping(route):
    def decorator(f):
        app.route(route, methods=['GET'])(f)
        return f

    return decorator


def post_mapping(route):
    def decorator(f):
        app.route(route, methods=['POST'])(f)
        return f

    return decorator
