# encoding: utf-8
from __future__ import unicode_literals
import string


class BaseTemplate(object):

    def __init__(self, template_text, **kwargs):
        self.set_template_text(template_text)
        self.kwargs = kwargs

    def set_template_text(self, template_text):
        self.template_text = template_text
        self._template = None

    def render(self, **kwargs):
        raise NotImplementedError

    def compile_template(self):
        raise NotImplementedError

    @property
    def template(self):
        if self._template is None:
            self._template = self.compile_template()
        return self._template


class StringTemplate(BaseTemplate):
    """
    string.Template based engine.
    """
    def compile_template(self):
        safe_substitute = self.kwargs.get('safe_substitute', True)
        t = string.Template(self.template_text)
        if safe_substitute:
            return t.safe_substitute
        else:
            return t.substitute

    def render(self, **kwargs):
        return self.template(**kwargs)