from dataclasses import dataclass, field

from .state import State


@dataclass
class ETL:
    state: State
    transform_pipeline: list = field(default=list())
    load_pipeline: list = field(default=list())
    extract_pipeline: list = field(default=list())

    def run(self):
        pipe_coro = None
        for pipe in self.extract_pipeline.reverse():
            pipe_coro = pipe(self.state, pipe_coro)
            next(pipe_coro)
