import inspect

from flask_context_manager.src.main.model.beans.base_bean import BaseBean


class Configuration(BaseBean):

    def start(self, context, bean):
        params = inspect.signature(bean.__init__).parameters
        kwargs = {'app': context.app} if 'app' in params else {}
        context.beans[self] = bean(**kwargs)
