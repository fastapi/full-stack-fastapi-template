# encoding: utf-8
from __future__ import unicode_literals
from .base import BaseTemplate


class JinjaTemplate(BaseTemplate):
    """
    This template is mostly for demo purposes.
    You probably want to subclass from it
    and make more clear environment initialization.
    """

    DEFAULT_JINJA_ENVIRONMENT = {}

    def __init__(self, template_text, environment=None):
        super(JinjaTemplate, self).__init__(template_text)
        if environment:
            self.environment = environment
        else:
            if 'jinja2' not in globals():
                globals()['jinja2'] = __import__('jinja2')
            self.environment = jinja2.Environment(**self.DEFAULT_JINJA_ENVIRONMENT)

    def compile_template(self):
        return self.environment.from_string(self.template_text)

    def render(self, **kwargs):
        return self.template.render(**kwargs)
