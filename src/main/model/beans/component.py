from src.main.model.beans.base_bean import BaseBean


class Component(BaseBean):

    def start(self, context, bean):
        context.beans[self] = bean()

