from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from .paths import ROOT


def render_template(template_path: Path, **kwargs):
    env = Environment(loader=FileSystemLoader(ROOT))
    template = env.get_template(str(template_path.relative_to(ROOT)))
    return template.render(**kwargs)
