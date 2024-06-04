import importlib
import inspect
import logging
import os
import textwrap
from functools import partial
from pathlib import Path
from typing import Optional, Callable, Any, TypeVar, Dict, TYPE_CHECKING, List, Set, Hashable, Type

import networkx as nx
from flask import request, Flask

from flask_context_manager.relative_path import RelativePath
from flask_context_manager.src.main.model.bean_wrapper import BeanWrapper, NamedParameter
from flask_context_manager.src.util.collection_util import flatten, get_or_put, first_or_none

if TYPE_CHECKING:
    from flask_context_manager.src.main.model.beans.bean import Bean

ROOT_DIR = "."

T = TypeVar("T")


class ContextManager:
    path = RelativePath("src/main/resources/settings.json")
    settings = path.read_json()

    if settings is None:
        raise RuntimeError("Could not read the 'settings.json' file, please try reinstalling the FCM package.")

    ignored = settings["ignored"]
    possible_annotations = settings["annotations"]
    log = logging.getLogger("ContextManager")
    app: Optional[Flask] = None
    beans: Dict[Hashable, Set[BeanWrapper]] = dict()
    instantiated_beans: Dict[str, object] = dict()
    imported_modules: List[str] = list()

    @classmethod
    def all_beans(cls):
        return flatten(cls.beans.values())

    @classmethod
    def checked_app(cls) -> Flask:
        if cls.app is None:
            raise RuntimeError("Tried to run app before setting it up with a Flask app.\nPlease use 'ContextManager.append(flask_app)'")
        return cls.app

    @classmethod
    def start(cls, production=False, debug=True, statistics=True):
        cls._import_all_modules()
        cls._start_all_modules()
        if statistics:
            cls.log_statistics()
        cls.checked_app().run(debug=debug)

    @classmethod
    def get_module_name_from_path(cls, path) -> str:
        rel_path = os.path.relpath(path).replace(os.sep, '.')
        module_name, _ = os.path.splitext(rel_path)
        return module_name

    @classmethod
    def _import_module_from_path(cls, file_path: str):
        file_txt = Path(file_path).read_text()
        found_annotations = (annotation in file_txt for annotation in cls.possible_annotations)

        if not any(found_annotations):
            return
        try:
            module_name = cls.get_module_name_from_path(file_path)
            importlib.import_module(module_name)
            cls.imported_modules.append(module_name)
        except Exception as e:
            raise e
            cls.log.error(f"Failed to import module named '{file_path}': '{e.with_traceback(None)}'")

    @classmethod
    def _import_all_modules(cls, filename: str | Path = ROOT_DIR):
        if not (isinstance(filename, Path) or isinstance(filename, str)):
            raise RuntimeError(f"Filename type not supported: '{type(filename)}'")

        if isinstance(filename, str):
            filename = Path(filename)

        for file in filename.iterdir():
            if file.is_dir():
                if cls.is_ignored(file):
                    continue
                cls._import_all_modules(file)
            else:
                if str(file).endswith('.py') and not cls.is_ignored(file):
                    cls._import_module_from_path(str(file))

    @classmethod
    def _start_all_modules(cls):
        graph = nx.DiGraph()
        bean_methods = flatten(cls.beans.values())
        for bean_method in list(bean_methods):
            graph.add_node(bean_method)

        for bean_method in list(bean_methods):
            dependencies = {dep.name for dep in bean_method.dependencies}
            for dependency in dependencies:
                dependency_providers = cls.beans.get(dependency, [])
                for dependency_provider in dependency_providers:
                    graph.add_edge(bean_method, dependency_provider)

        ordered_bean_methods: List[BeanWrapper] = list(nx.topological_sort(graph))

        for bean in ordered_bean_methods:
            new_instance = cls._get_instance_by_bean_wrapper(bean)
            bean.instance = new_instance

    @classmethod
    def get_bean_parameters(cls, obj: type) -> List[NamedParameter]:
        instance_fun = obj.__init__

        if inspect.isfunction(obj) or inspect.ismethod(obj):
            instance_fun = obj

        sig = inspect.signature(instance_fun)
        kwargs = []
        items = list(sig.parameters.items())
        for name, param in items:
            if name == 'self' or ContextManager._inspection_is_empty(param):
                continue
            annotation = instance_fun.__annotations__[name]
            if hasattr(annotation, "child_class"):
                annotation = annotation.child_class
            kwargs.append(NamedParameter(name=name, key=annotation))
        return kwargs

    @classmethod
    def _inspection_is_empty(cls, param):
        return param.annotation == param.empty

    @classmethod
    def is_function_or_method(cls, element):
        return inspect.isfunction(element) or inspect.ismethod(element)

    @classmethod
    def register_routes(cls, controller):
        prefix = getattr(controller, "_route_prefix", "")
        for method_name, method in inspect.getmembers(controller, predicate=cls.is_function_or_method):
            route = getattr(method, "_route", None)
            methods: Optional[Callable] = getattr(method, "_methods", None)
            if route is not None and methods is not None:
                wrapped_method = partial(cls._handle_request_body, method)
                new_method_name = method_name + '_wrapped'
                setattr(wrapped_method, "__name__", new_method_name)
                route_path = cls.append_prefix(prefix, route)
                cls.checked_app().route(route_path, methods=methods)(wrapped_method)

    @classmethod
    def append_prefix(cls, prefix, route):
        paths = prefix.split('/') + route.split('/')
        paths = [p for p in paths if p != ""]
        route_path = "/" + "/".join(paths)
        return route_path

    @classmethod
    def append(cls, app):
        cls.app = app
        return cls

    @classmethod
    def _get_dependency(cls, annotation, obj) -> object:
        if annotation == obj:
            raise RuntimeError(f"Circular dependency detected for service {obj.__name__}")

        instantiated_beans = [bean for bean in cls.beans.values() if not isinstance(bean, type)]
        dependency_dict = {bean.__class__: bean for bean in instantiated_beans}

        try:
            return dependency_dict[annotation]
        except RuntimeError:
            raise RuntimeError(f"Dependency '{annotation}' not found for object '{obj.__name__}'")

    @staticmethod
    def _handle_request_body(method: Callable[[Any], T], *args, **kwargs) -> T:
        if request.method != 'GET':
            request_body = request.json or {}
            new_kwargs = {param: request_body.get(param, None) for param in inspect.signature(method).parameters}
            new_kwargs.update(kwargs)
        else:
            new_kwargs = kwargs
        return method(*args, **new_kwargs)

    @classmethod
    def instance(cls, obj_type: Type[T]) -> Optional[T]:
        return cls._get_instance_by_bean_type(obj_type)

    @classmethod
    def _get_instance_by_bean_wrapper(cls, bean_wrapper: BeanWrapper):
        dependencies = bean_wrapper.dependencies
        preloaded = bean_wrapper.bean_method
        if bean_wrapper.is_method and bean_wrapper.bean_class is not None:
            current_instance = cls.instance(bean_wrapper.bean_class.return_type)
            if current_instance is None:
                raise RuntimeError(f"Could not identify an instantiated source class of type '{bean_wrapper.bean_class.return_type}' for bean '{bean_wrapper.bean_name}'")
            preloaded = partial(bean_wrapper.bean_method, current_instance)
        return cls._get_instance_by_named_parameter(dependencies, preloaded)

    @staticmethod
    def _is_dependency(bean_wrapper: BeanWrapper, named_parameter: NamedParameter):
        return bean_wrapper.bean_name == named_parameter.name \
            or bean_wrapper.return_type == named_parameter.key \
            or bean_wrapper.return_type == named_parameter.name

    @classmethod
    def _get_instance_by_bean_type(cls, obj_type: Type[T]) -> Optional[T]:
        bean_parameters = cls.get_bean_parameters(obj_type)
        return cls._get_instance_by_named_parameter(bean_parameters, obj_type)

    @classmethod
    def _get_instance_by_named_parameter(cls, dependencies: List[NamedParameter], bean_method: Callable[..., T]) -> T:
        injections: Dict[str, object] = dict()

        for dependency in dependencies:
            current_dependency = first_or_none(cls.all_beans(), lambda item: cls._is_dependency(item, dependency))
            if current_dependency is None or current_dependency.instance is None:
                raise RuntimeError(f"Could not find '{dependency.name}' dependency for bean method '{bean_method}'")
            injections[dependency.name] = current_dependency.instance
        new_instance = bean_method(**injections)
        return new_instance

    @classmethod
    def is_ignored(cls, path) -> bool:
        return any(pattern in str(path) for pattern in cls.ignored)

    @classmethod
    def add_bean(cls, bean: Type[T]):
        wrapped = BeanWrapper(
            bean_name=bean.__name__,
            parameters=cls.get_bean_parameters(bean),
            bean_method=bean,
            return_type=bean,
        )
        cls.add_to_bean_map(wrapped.return_type, wrapped)

    @classmethod
    def add_config_bean(cls, bean: "Bean", child_class, return_type):
        bean_class = first_or_none(cls.all_beans(), lambda it: it.return_type == child_class)
        wrapped = BeanWrapper(
            bean_name=bean.fun.__name__,
            parameters=cls.get_bean_parameters(bean.fun),
            bean_method=bean.fun,
            return_type=return_type or bean.fun.__name__,
            bean_class=bean_class,
            is_method=True,
        )
        cls.add_to_bean_map(return_type, wrapped)

    @classmethod
    def add_to_bean_map(cls, bean_type: type, bean):
        current_beans = get_or_put(cls.beans, bean_type, lambda: {bean})
        current_beans.add(bean)

    @classmethod
    def log_statistics(cls):
        statistics = f"""
        ########################################################## 
        ############ Flask Context Manager Statistics ############ 
        ########################################################## 
         
        Imported Modules ({len(cls.imported_modules)}):
            {ContextManager.bullet_print(cls.imported_modules)} 
             
        Identified Beans:
            {ContextManager.bullet_print(list(map(lambda it: f"{it.bean_name} -> {it.return_type}", cls.all_beans())))} 
             
        Registered routes:
            {ContextManager.bullet_print(cls.checked_app().url_map.iter_rules())}  
        
        ########################################################## 
        """
        print(textwrap.dedent(statistics.replace("\t", " " * 4)))

    @classmethod
    def bullet_print(cls, iterable):
        iterable = list(filter(lambda it: it is not None, iterable))

        if not iterable:
            return ""

        def _get_str(current):
            return getattr(current, str("__name__"), str(current))

        names = sorted(set(map(lambda k: "- " + _get_str(k), iterable)), key=lambda it: it.lower())
        text = "\n\t\t\t".join(names)
        return text
