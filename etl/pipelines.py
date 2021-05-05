import inspect
import itertools
from dataclasses import dataclass, field


class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


@dataclass
class Executor(metaclass=Singleton):
    context: dict = field(default_factory=dict)
    pipelines: dict = field(default_factory=dict)

    def __post_init__(self):
        self._root_pipelines = []

    def _init_context(self, context):
        context, source_context = itertools.tee(context)
        for context_obj in context:
            if all(src in self.context for src in context_obj._source):
                value = context_obj(**{itm: self.context.get(itm) for itm in context_obj._source})
                self.context.update({context_obj._name: value})
                self._init_context(filter(lambda itm: itm._name not in self.context, source_context))

    def _init_pipelines(self, pipelines):
        def init_pipeline(pipeline, pipelines):
            pipelines, children_pipelines = itertools.tee(pipelines)
            for child in filter(lambda itm: itm._source == pipeline._name, children_pipelines):
                if child._name not in self.pipelines:
                    pipelines, children_pipelines = itertools.tee(pipelines)
                    child = init_pipeline(child, children_pipelines)
                    coro = child()
                    next(coro)
                    self.pipelines.update({child._name: coro})
                else:
                    coro = self.pipelines.get(child._name)
                pipeline._add_children(coro)
            return pipeline

        pipelines, root_pipelines = itertools.tee(pipelines)
        for pipeline_obj in filter(lambda itm: itm._source is None, root_pipelines):
            pipelines, children_pipelines = itertools.tee(pipelines)
            root_pipeline = init_pipeline(pipeline_obj, children_pipelines)
            root_coro = root_pipeline()
            next(root_coro)
            self._root_pipelines.append(root_coro)

    def run(self, module):
        context = (attr for name, attr in inspect.getmembers(module) if isinstance(attr, Context))
        self._init_context(context)

        pipelines = (attr for name, attr in inspect.getmembers(module) if isinstance(attr, Pipeline))
        self._init_pipelines(pipelines)

        while True:
            for pipeline in self._root_pipelines:
                next(pipeline)


class Pipeline:
    def __init__(self, func, source=None):
        self._func = func
        self._source = source
        self._name = func.__name__
        self._children = set()
        self._context = None

    def _add_children(self, *children):
        self._children = self._children | set(children)
        return self._children

    @property
    def context(self):
        if self._context is None:
            executor = Executor()
            spec = inspect.getfullargspec(self._func)
            self._context = {name: executor.context[name] for name in spec.args if name != 'data'}
        return self._context

    def __call__(self):
        while True:
            data = (yield)
            result = self._func(data, **self.context)
            for child in self._children:
                if child is not None:
                    child.send(result)


class IPipeline(Pipeline):
    def __call__(self, *args, **kwargs):
        while True:
            data = (yield)
            for item in data:
                result = self._func(item, **self.context)
                for child in self._children:
                    if child is not None:
                        child.send(result)


def pipeline(source=None):
    def wrapper(func):
        return Pipeline(func, source)
    return wrapper


def ipipeline(source=None):
    def wrapper(func):
        return IPipeline(func, source)
    return wrapper


class Context:
    def __init__(self, func):
        self._func = func
        self._name = func.__name__
        spec = spec = inspect.getfullargspec(self._func)
        self._source = spec.args

    @property
    def context(self):
        executor = Executor()
        return {name: executor.context[name] for name in self._source}

    def __call__(self, *args, **kwargs):
        return self._func(**self.context)


def context(func):
    return Context(func)
