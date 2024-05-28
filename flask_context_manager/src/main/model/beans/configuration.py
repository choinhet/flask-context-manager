import inspect

from flask_context_manager.src.main.model.beans.base_bean import BaseBean
from flask_context_manager.src.main.model.beans.bean import Bean


class Configuration(BaseBean):

    def start(self, context, bean):
        params = inspect.signature(bean.__init__).parameters
        with_app = {'app': context.app} if 'app' in params else {}
        kwargs = context.get_injections(bean).update(with_app) or {}
        class_instance = bean(**kwargs)
        members = inspect.getmembers(class_instance)
        beans = list(filter(lambda it: issubclass(type(it), Bean), map(lambda it: it[1], members)))
        for bean in beans:
            current_injections = context.get_injections(bean.fun)
            result = bean(class_instance, **current_injections)
            if result is None:
                continue
            return_type = bean.fun.__annotations__.get("return") or type(result)
            context.beans[return_type] = result
            context.beans[bean.fun.__name__] = result
