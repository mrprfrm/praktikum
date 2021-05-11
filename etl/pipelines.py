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

    def _init_context(self, context):
        context, source_context = itertools.tee(context)
        for context_obj in context:
            if all(src in self.context for src in context_obj._source):
                value = context_obj(**{itm: self.context.get(itm) for itm in context_obj._source})
                self.context.update({context_obj._name: value})
                self._init_context(filter(lambda itm: itm._name not in self.context, source_context))

    def _init_pipelines(self, pipelines):
        pipelines_map = {itm._name: itm for itm in pipelines}

        def init_pipeline(pipeline, next_pipeline=None):
            coro = pipeline(next_pipeline)
            next(coro)
            if pipeline._prev is not None:
                prev_pipeline = pipelines_map[pipeline._prev]
                return init_pipeline(prev_pipeline, coro)
            return coro


        prev_names = [itm._prev for itm in pipelines_map.values() if itm._prev is not None]
        for pipeline in filter(lambda itm: itm._name not in prev_names, pipelines_map.values()):
            yield init_pipeline(pipeline)

    def run(self, module):
        context = (attr for name, attr in inspect.getmembers(module) if isinstance(attr, Context))
        self._init_context(context)

        pipelines = (attr for name, attr in inspect.getmembers(module) if isinstance(attr, Pipeline))
        root_pipelines = list(self._init_pipelines(pipelines))

        while True:
            for pipeline in root_pipelines:
                next(pipeline)


class Pipeline:
    def __init__(self, func, prev=None):
        self._func = func
        self._prev = prev
        self._name = func.__name__
        self._context = None

    @property
    def executor(self):
        return Executor()

    @property
    def context(self):
        if self._context is None:
            spec = inspect.getfullargspec(self._func)
            self._context = {name: self.executor.context[name] for name in spec.args if name != 'data'}
        return self._context

    def __call__(self, next_pipeline=None):
        while True:
            data = (yield)
            result = self._func(data, **self.context)
            if next_pipeline is not None:
                next_pipeline.send(result)

class IPipeline(Pipeline):
    def __init__(self, func, prev=None, source=None):
        super(IPipeline, self).__init__(func, prev)
        self._source = source

    def __call__(self, next_pipeline=None, *args, **kwargs):
        while True:
            data = (yield)
            try:
                if self._source is None:
                    item = next(data)
                elif self._source in self.executor.context:
                    item = next(self.executor.context[self._source])
                else:
                    raise AttributeError(f'No context with name {self._source} exists')

                result = self._func(item, **self.context)
                if next_pipeline is not None:
                    next_pipeline.send(result)
            except StopIteration:
                pass


def pipeline(prev=None):
    def wrapper(func):
        return Pipeline(func, prev)
    return wrapper


def ipipeline(prev=None, source=None):
    def wrapper(func):
        return IPipeline(func, prev, source)
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
