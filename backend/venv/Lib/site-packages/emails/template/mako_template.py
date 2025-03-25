# encoding: utf-8
from __future__ import unicode_literals
from .base import BaseTemplate


class MakoTemplate(BaseTemplate):

    def compile_template(self):
        if 'mako_template' not in globals():
            globals()['mako_template'] = __import__('mako.template')
        return mako_template.template.Template(self.template_text)

    def render(self, **kwargs):
        return self.template.render(**kwargs)
