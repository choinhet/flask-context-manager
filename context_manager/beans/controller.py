from context_manager.beans.base_bean import BaseBean


class Controller(BaseBean):

    def start(self, context, bean):
        kwargs = context.get_injections(bean)
        context.beans[self] = bean(**kwargs)
        context.register_routes(context.beans[self])

