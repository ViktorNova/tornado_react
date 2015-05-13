#! -*- coding: utf-8 -*-

import os

import tornado.web

from jinja2 import Environment, ChoiceLoader, FileSystemLoader, FunctionLoader, TemplateNotFound

from react.jsx import JSXTransformer, TransformError

import settings

# def react_component_loader(name):
#     """ """
#     print(name)
#     try:
#         return JSXTransformer().transform_string(name)
#     except TransformError as e:
#         raise CompilerError(str(e))

class ReactFileSystemStringLoader(FileSystemLoader):

    def get_source(self, environment, template):
        contents, filename, uptodate  = super(ReactFileSystemStringLoader, self).get_source(environment, template)
        contents = JSXTransformer().transform_string(contents)
        print("REACCCTTTTTTTTTTTTT")
        print("REACCCTTTTTTTTTTTTT", contents)
        return contents, filename, uptodate


# class ReactFileSystemStringTransformer(FileSystemLoader):
#     def get_source(self, environment, template):
#         contents, filename, uptodate  = super(ReactFileSystemStringTransformer, self).get_source(environment, template)

#         outfile = os.path.join(settings.settings["static_js_path"], os.path.basename(filename))

#         print("", outfile)
#         js = JSXTransformer().transform_string(contents)
#         with open(outfile, 'wb') as o:
#             o.write(js.encode('utf8'))
#         to_template = "<script src='{{ static_url('js/%s') }}'></script>" % filename
#         print(to_template)
#         return to_template, filename, uptodate

def React_FileSystem_String_Transformer(name):

        infile = os.path.join(settings.settings["react_components_dir"], os.path.basename(name))
        outfile = os.path.join(settings.settings["static_js_path"], os.path.basename(name))

        js = JSXTransformer().transform(infile, outfile)
        to_template = "<script src='{{ static_url('js/%s') }}'></script>" % name

        return to_template


class TemplateRendering(object):
    """
    A simple class to hold methods for rendering templates.
    """
    def render_template(self, template_name, **kwargs):
        templates_dir = []
        if self.settings.get('templates_html', ''):
            templates_dir.append(
                self.application.settings["templates_html"]
            )

        react_components_dir = self.application.settings["react_components_dir"]

        env = Environment(loader=ChoiceLoader([
            FileSystemLoader(templates_dir),
            FunctionLoader(React_FileSystem_String_Transformer),
        ]))

        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(template_name)
        content = template.render(kwargs)
        return content


class BaseHandler(tornado.web.RequestHandler, TemplateRendering):
    """
    RequestHandler already has a `render()` method. I'm writing another
    method `render_jinja()` and keeping the API almost same.
    """
    def render_jinja(self, template_name, **kwargs):
        """
        This is for making some extra context variables available to
        the template
        """
        kwargs.update({
            'settings': self.application.settings,
            'static_url': self.static_url,
            'request': self.request,
            'xsrf_token': self.xsrf_token,
            'xsrf_form_html': self.xsrf_form_html,
        })
        self.write(self.render_template(template_name, **kwargs))

class JSONBaseHandler(BaseHandler):
    pass

class MainHandler(BaseHandler):
    def get(self):
        print("GET")
        self.render_jinja("basic.html")

class CommentsHandler(BaseHandler):
    def get(self):
        self.render_jinja("comments.html")


class CommentsDataHandler(tornado.web.RequestHandler):
    def get(self):
        data = { "data": [
            { "author": "Pete Hunt", "text": "This is one comment"},
            { "author": "Jordan Walke", "text": "This is *another* comment"}
        ]}
        print("api/CommentsHandler")
        self.write(data)