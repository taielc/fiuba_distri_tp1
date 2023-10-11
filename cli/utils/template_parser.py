from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from paths import ROOT_DIR


def render_template(template_path: Path, **kwargs):
    env = Environment(loader=FileSystemLoader(ROOT_DIR))
    template = env.get_template(str(template_path.relative_to(ROOT_DIR)))
    return template.render(**kwargs)
