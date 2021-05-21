from os import path
from jinja2 import FileSystemLoader, Environment, Markup, contextfunction

@contextfunction
def include_file(ctx, name):
    env = ctx.environment
    return Markup(env.loader.get_source(env, name)[0])

def get_env():
    env = Environment(loader=FileSystemLoader(path.dirname(__file__)))
    env.globals['include_file'] = include_file
    return env