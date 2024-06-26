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
from waitress import serve

from flask_context_manager.relative_path import RelativePath
from flask_context_manager.src.main.model.bean_wrapper import BeanWrapper, NamedParameter
from flask_context_manager.src.util.collection_util import flatten, get_or_put, first_or_none

if TYPE_CHECKING:
    from flask_context_manager.src.main.model.beans.base_bean import BaseBean
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
            cls.log_statistics()
            raise RuntimeError("Tried to run app before setting it up with a Flask app.\nPlease use 'ContextManager.append(flask_app)'")
        return cls.app

    @classmethod
    def start(
        cls,
        debug=True,
        host="127.0.0.1",
        port=8080,
        production=False,
        statistics=True,
    ):
        cls._import_all_modules()
        cls._start_all_modules()
        if statistics:
            cls.log_statistics()
        if production:
            serve(cls.checked_app(), host=host, port=port)
        else:
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
            cls.log.error(f"Failed to import module named '{file_path}': '{e.with_traceback(None)}'")

    @classmethod
    def _import_all_modules(cls, filename: str | Path = ROOT_DIR):
        if not (isinstance(filename, Path) or isinstance(filename, str)):
            cls.log_statistics()
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
        for bean in list(cls.all_beans()):
            graph.add_node(bean)

        for bean in list(cls.all_beans()):
            dependencies = {dep.clazz for dep in bean.dependencies}
            for dependency in dependencies:
                dependency_providers = cls.beans.get(dependency, [])
                for dependency_provider in dependency_providers:
                    graph.add_edge(bean, dependency_provider)

        cls._check_for_circular_dependency(graph)
        nodes: List[BeanWrapper] = list(nx.topological_sort(graph))
        ordered_bean_methods = cls.sort_by_dependencies(nodes)

        for bean in ordered_bean_methods:
            new_instance = cls._get_instance_by_bean_wrapper(bean)
            bean.instance = new_instance
            if bean.super_class is None:
                continue
            current_super_class_name = bean.super_class.__class__.__name__
            if current_super_class_name == "Controller":
                cls.register_routes(new_instance)

    @classmethod
    def _check_for_circular_dependency(cls, graph):
        try:
            cycle = nx.find_cycle(graph, orientation='original')
            raise RuntimeError(f"Circular dependency found: {cycle}")
        except:
            """
            This is the expected scenario, it's kind of weird.
            """

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
            kwargs.append(NamedParameter(name=name, clazz=annotation))
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
                cls.log_statistics()
                raise RuntimeError(f"Could not identify an instantiated source class of type '{bean_wrapper.bean_class.return_type}' for bean '{bean_wrapper.bean_name}'")
            preloaded = partial(bean_wrapper.bean_method, current_instance)
        return cls._get_instance_by_named_parameter(dependencies, preloaded)

    @classmethod
    def _is_dependency(cls, bean_wrapper: BeanWrapper, named_parameter: NamedParameter):
        return bean_wrapper.bean_name == named_parameter.name \
            or cls._handle_class_type(bean_wrapper.return_type) == cls._handle_class_type(named_parameter.clazz)

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
                cls.log_statistics()
                raise RuntimeError(f"Could not find '{dependency.name}' with type '{dependency.clazz}' dependency for bean method '{bean_method}'")
            injections[dependency.name] = current_dependency.instance
        new_instance = bean_method(**injections)
        return new_instance

    @classmethod
    def is_ignored(cls, path) -> bool:
        return any(pattern in str(path) for pattern in cls.ignored)

    @classmethod
    def add_bean(cls, bean: Type[T], super_class: "BaseBean"):
        wrapped = BeanWrapper(
            bean_name=bean.__name__,
            parameters=cls.get_bean_parameters(bean),
            bean_method=bean,
            return_type=bean,
            super_class=super_class,
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
            {ContextManager.bullet_print(list(map(lambda it: f"{it.bean_name} -> {it.return_type} -> {'OK' if it.instance else 'NOT INSTANTIATED'}", cls.all_beans())))} 
             
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

    @classmethod
    def _is_super_class_of(cls, clazz1, clazz2):
        clazz1 = cls._handle_class_type(clazz1)
        clazz2 = cls._handle_class_type(clazz2)
        args = [clazz1, clazz2]
        if not isinstance(clazz1, type) or not isinstance(clazz2, type):
            return False
        return issubclass(clazz2, clazz1)

    @classmethod
    def _handle_class_type(cls, clazz):
        clazz = getattr(clazz, "__origin__", clazz)
        if isinstance(clazz, str):
            beans = cls.all_beans()
            matched_class = first_or_none(beans, lambda it: getattr(it.return_type, "__name__", it.bean_name) == clazz or it.bean_name == clazz)
            if matched_class is not None and isinstance(matched_class.return_type, type):
                return matched_class.return_type
        return clazz

    @classmethod
    def sort_by_dependencies(cls, bean_methods: List[BeanWrapper]) -> List[BeanWrapper]:
        if len(bean_methods) <= 1:
            return bean_methods[:]

        list_ = bean_methods[:]
        last_index = len(list_) - 1

        for k in range(len(list_)):
            swapped = False
            for i in range(last_index):
                for j in range(i + 1, len(list_)):
                    item1 = list_[i]
                    item2 = list_[j]

                    should_invert_based_on_dependency = any(cls._is_super_class_of(dep.clazz, item2.return_type) for dep in item1.dependencies)
                    does_not_depend_inversely = all(not cls._is_super_class_of(dep.clazz, item1.return_type) for dep in item2.dependencies)
                    should_invert_based_on_size = does_not_depend_inversely and len(item1.dependencies) > len(item2.dependencies)

                    if should_invert_based_on_dependency or should_invert_based_on_size:
                        list_[i], list_[j] = list_[j], list_[i]
                        swapped = True
            if not swapped:
                break

        return list_

    @classmethod
    def endpoint_map(cls):
        base_map = list(cls.checked_app().url_map.iter_rules())
        url_list = list(filter(lambda it: it != "/", map(str, base_map)))
        return url_list
