"""
Pane class which render various markup languages including HTML,
Markdown, and also regular strings.
"""
from __future__ import absolute_import, division, unicode_literals

try:
    from html import escape
except:
    from cgi import escape
from six import string_types

import param

from bokeh.models import Div as _BkDiv

from ..viewable import Layoutable
from ..models import HTML as _BkHTML
from .base import PaneBase


class DivPaneBase(PaneBase):
    """
    Baseclass for Panes which render HTML inside a Bokeh Div.
    See the documentation for Bokeh Div for more detail about
    the supported options like style and sizing_mode.
    """

    # DivPane supports updates to the model
    _updates = True

    __abstract = True

    style = param.Dict(default=None, doc="""
        Dictionary of CSS property:value pairs to apply to this Div.""")

    _rename = {'object': 'text'}

    _bokeh_model = _BkDiv

    def _get_properties(self):
        props = {p : getattr(self, p) for p in list(Layoutable.param) + ['style']
                 if getattr(self, p) is not None}
        if self.sizing_mode not in ['fixed', None]:
            if 'style' not in props:
                props['style'] = {}
            props['style'].update(width='100%', height='100%')
        return props

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = self._bokeh_model(**self._get_properties())
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update(self, model):
        model.update(**self._get_properties())


class HTML(DivPaneBase):
    """
    HTML panes wrap HTML text in a bokeh Div model.  The
    provided object can either be a text string, or an object that
    has a `_repr_html_` method that can be called to get the HTML
    text string.  The height and width can optionally be specified, to
    allow room for whatever is being wrapped.
    """

    # Priority is dependent on the data type
    priority = None

    _bokeh_model = _BkHTML

    @classmethod
    def applies(cls, obj):
        module, name = getattr(obj, '__module__', ''), type(obj).__name__
        if ((any(m in module for m in ('pandas', 'dask')) and
            name in ('DataFrame', 'Series')) or hasattr(obj, '_repr_html_')):
            return 0.2
        elif isinstance(obj, string_types):
            return None
        else:
            return False

    def _get_properties(self):
        properties = super(HTML, self)._get_properties()
        text = '' if self.object is None else self.object
        if hasattr(text, '_repr_html_'):
            text = text._repr_html_()
        return dict(properties, text=escape(text))


class DataFrame(HTML):
    """
    DataFrame renders pandas, dask and streamz DataFrame types using
    their custom HTML repr. In the case of a streamz DataFrame the
    rendered data will update periodically.
    """

    _object = param.Parameter(default=None)

    _rerender_params = ['object', '_object']

    def __init__(self, object=None, **params):
        super(DataFrame, self).__init__(object, **params)
        self._stream = None
        self._setup_stream()

    @classmethod
    def applies(cls, obj):
        if (any(obj.__module__ for m in ('pandas', 'dask', 'streamz')) and
            type(obj).__name__ in ('DataFrame', 'Series', 'Random')):
            return 0.3
        else:
            return False

    def _set_object(self, object):
        self._object = object

    @param.depends('object', watch=True)
    def _setup_stream(self):
        if not self._models or not hasattr(self.object, 'stream'):
            return
        elif self._stream:
            self._stream.destroy()
            self._stream = None
        self._stream = self.object.stream.latest().rate_limit(0.5).gather()
        self._stream.sink(self._set_object)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = super(DataFrame, self)._get_model(doc, root, parent, comm)
        self._setup_stream()
        return model

    def _cleanup(self, model):
        super(DataFrame, self)._cleanup(model)
        if not self._models and self._stream:
            self._stream.destroy()
            self._stream = None

    def _get_properties(self):
        properties = DivPaneBase._get_properties(self)
        if self._stream:
            df = self._object
        else:
            df = self.object
        if hasattr(df, 'to_frame'):
            df = df.to_frame()
        if hasattr(df, 'to_html'):
            text = df.to_html(classes=['panel-df']).replace('border="1"', '')
        else:
            text = ''
        return dict(properties, text=escape(text))


class Str(DivPaneBase):
    """
    A Str pane renders any object for which `str()` can be called,
    escaping any HTML markup and then wrapping the resulting string in
    a bokeh Div model.  Set to a low priority because generally one
    will want a better representation, but allows arbitrary objects to
    be used as a Pane (numbers, arrays, objects, etc.).
    """

    priority = 0

    @classmethod
    def applies(cls, obj):
        return True

    def _get_properties(self):
        properties = super(Str, self)._get_properties()
        if self.object is None:
            text = ''
        else:
            text = '<pre>'+escape(str(self.object))+'</pre>'
        return dict(properties, text=text)


class Markdown(DivPaneBase):
    """
    A Markdown pane renders the markdown markup language to HTML and
    displays it inside a bokeh Div model. It has no explicit
    priority since it cannot be easily be distinguished from a
    standard string, therefore it has to be invoked explicitly.
    """

    # Priority depends on the data type
    priority = None

    @classmethod
    def applies(cls, obj):
        if hasattr(obj, '_repr_markdown_'):
            return 0.3
        elif isinstance(obj, string_types):
            return 0.1
        else:
            return False

    def _get_properties(self):
        import markdown
        data = self.object
        if data is None:
            data = ''
        elif not isinstance(data, string_types):
            data = data._repr_markdown_()
        properties = super(Markdown, self)._get_properties()
        properties['style'] = properties.get('style', {})
        extensions = ['markdown.extensions.extra', 'markdown.extensions.smarty']
        html = markdown.markdown(data, extensions=extensions, output_format='html5')
        return dict(properties, text=html)
