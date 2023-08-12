from context_manager.beans.base_bean import BaseBean


class Service(BaseBean):
    def __init__(self, cls):
        super().__init__(cls)

    def start(self, context, bean):
        kwargs = context.get_injections(bean)
        context.beans[self] = bean(**kwargs)
