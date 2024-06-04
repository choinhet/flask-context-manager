from flask_context_manager import Controller, ContextManager, get_mapping


@Controller
class HomeController:

    @get_mapping("/")
    def home(self):
        return ContextManager.endpoint_map()
