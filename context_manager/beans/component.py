from context_manager.beans.base_bean import BaseBean


class Component(BaseBean):
    def __init__(self, cls):
        super().__init__(cls)

    def start(self, context, bean):
        context.beans[self] = bean()

