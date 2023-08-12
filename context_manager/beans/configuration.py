import inspect

from context_manager.beans.base_bean import BaseBean


class Configuration(BaseBean):
    def __init__(self, cls):
        super().__init__(cls)

    def start(self, context, bean):
        params = inspect.signature(bean.__init__).parameters
        kwargs = {'app': context.app} if 'app' in params else {}
        context.beans[self] = bean(**kwargs)
