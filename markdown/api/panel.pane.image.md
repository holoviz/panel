# panel.pane.image module

Contains Image panes including renderers for PNG, SVG, GIF and JPG file
types.

class panel.pane.image.AVIF(object=None, **params)
Bases: [ImageBase](#panel.pane.image.ImageBase)

The AVIF pane embeds a .avif image file in a panel if provided a local
path, or will link to a remote image if provided a URL.

Reference: [https://panel.holoviz.org/reference/panes/AVIF.html](https://panel.holoviz.org/reference/panes/AVIF.html)

Example:

\>\>\>
AVIF(
...
'https://assets.holoviz.org/panel/samples/avif_sample.avif',
...
alt_text='A
nice tree', ...
link_url='https://en.wikipedia.org/wiki/AVIF',
...
width=500
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [class="reference internal" title="panel.pane.markup.HTMLBasePane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
> [title="panel.pane.image.FileBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](#panel.pane.image.FileBase):
> embed
>
> [title="panel.pane.image.ImageBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.ImageBase](#panel.pane.image.ImageBase):
> alt_text, caption, fixed_aspect, link_url, target
>
>

class panel.pane.image.FileBase(object=None, **params)
Bases: [HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane)

Methods

|  |  |
|----|----|
| [applies](#panel.pane.image.FileBase.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [class="reference internal" title="panel.pane.markup.HTMLBasePane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
>

`embed`` ``=`` ``Boolean(default=False,`` ``label='Embed')`
Whether to embed the file as base64.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.image.GIF(object=None, **params)
Bases: [ImageBase](#panel.pane.image.ImageBase)

The GIF pane embeds a .gif image file in a panel if provided a local
path, or will link to a remote image if provided a URL.

Reference: [https://panel.holoviz.org/reference/panes/GIF.html](https://panel.holoviz.org/reference/panes/GIF.html)

Example:

\>\>\>
GIF(
...
'https://upload.wikimedia.org/wikipedia/commons/b/b1/Loading_icon.gif',
...
alt_text='A
loading spinner', ...

link_url='https://commons.wikimedia.org/wiki/File:Loading_icon.gif',
...
width=500
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [class="reference internal" title="panel.pane.markup.HTMLBasePane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
> [title="panel.pane.image.FileBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](#panel.pane.image.FileBase):
> embed
>
> [title="panel.pane.image.ImageBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.ImageBase](#panel.pane.image.ImageBase):
> alt_text, caption, fixed_aspect, link_url, target
>
>

class panel.pane.image.ICO(object=None, **params)
Bases: [ImageBase](#panel.pane.image.ImageBase)

The ICO pane embeds an .ico image file in a panel if provided a local
path, or will link to a remote image if provided a URL.

Reference: [https://panel.holoviz.org/reference/panes/ICO.html](https://panel.holoviz.org/reference/panes/ICO.html)

Example:

\>\>\>
ICO(
...
some_url,
...
alt_text='An
.ico file', ...
link_url='https://en.wikipedia.org/wiki/ICO\_(file_format)',
...
width=50
...

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [class="reference internal" title="panel.pane.markup.HTMLBasePane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
> [title="panel.pane.image.FileBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](#panel.pane.image.FileBase):
> embed
>
> [title="panel.pane.image.ImageBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.ImageBase](#panel.pane.image.ImageBase):
> alt_text, caption, fixed_aspect, link_url, target
>
>

class panel.pane.image.Image(object=None, **params)
Bases: [ImageBase](#panel.pane.image.ImageBase)

The Image pane embeds any known image format in a panel if provided a
local path, bytes or remote image link.

Example:

\>\>\>
Image(
...
'https://panel.holoviz.org/\_static/logo_horizontal.png',
...
alt_text='The
Panel Logo', ...
link_url='https://panel.holoviz.org/index.html',
...
width=500
... )

Methods

|  |  |
|----|----|
| [applies](#panel.pane.image.Image.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [class="reference internal" title="panel.pane.markup.HTMLBasePane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
> [title="panel.pane.image.FileBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](#panel.pane.image.FileBase):
> embed
>
> [title="panel.pane.image.ImageBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.ImageBase](#panel.pane.image.ImageBase):
> alt_text, caption, fixed_aspect, link_url, target
>
>

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.image.ImageBase(object=None, **params)
Bases: [FileBase](#panel.pane.image.FileBase)

Encodes an image as base64 and wraps it in a Bokeh Div model. This is an
abstract base class that needs the image type to be specified and
specific code for determining the image shape.

The filetype determines the filetype, extension, and MIME type for this
image. Each image type (png,jpg,gif) has a base class that supports
anything with a \_repr_X\_ method (where X is png, gif, etc.), a local
file with the given file extension, or a HTTP(S) url with the given
extension. Subclasses of each type can provide their own way of
obtaining or generating a PNG.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [class="reference internal" title="panel.pane.markup.HTMLBasePane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
> [title="panel.pane.image.FileBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](#panel.pane.image.FileBase):
> embed
>
>

`alt_text`` ``=`` ``String(allow_None=True,`` ``label='Alt`` ``text')`
alt text to add to the image tag. The alt text is shown when a user
cannot load or display the image.

`caption`` ``=`` ``String(allow_None=True,`` ``label='Caption')`
Optional caption for the image.

`fixed_aspect`` ``=`` ``Boolean(default=True,`` ``label='Fixed`` ``aspect')`
Whether the aspect ratio of the image should be forced to be equal.

`link_url`` ``=`` ``String(allow_None=True,`` ``label='Link`` ``url')`
A link URL to make the image clickable and link to some other website.

`target`` ``=`` ``String(default='_blank',`` ``label='Target')`
The target attribute specifies where to open the linked document. It can
be \_self (default), \_blank, etc.

class panel.pane.image.JPG(object=None, **params)
Bases: [ImageBase](#panel.pane.image.ImageBase)

The JPG pane embeds a .jpg or .jpeg image file in a panel if provided a
local path, or will link to a remote image if provided a URL.

Reference: [https://panel.holoviz.org/reference/panes/JPG.html](https://panel.holoviz.org/reference/panes/JPG.html)

Example:

\>\>\>
JPG(
...
'https://www.gstatic.com/webp/gallery/4.sm.jpg',
...
alt_text='A
nice tree', ...
link_url='https://en.wikipedia.org/wiki/JPEG',
...
width=500
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [class="reference internal" title="panel.pane.markup.HTMLBasePane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
> [title="panel.pane.image.FileBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](#panel.pane.image.FileBase):
> embed
>
> [title="panel.pane.image.ImageBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.ImageBase](#panel.pane.image.ImageBase):
> alt_text, caption, fixed_aspect, link_url, target
>
>

class panel.pane.image.PDF(object=None, **params)
Bases: [FileBase](#panel.pane.image.FileBase)

The PDF pane embeds a .pdf image file in a panel if provided a local
path, or will link to a remote image if provided a URL.

Reference: [https://panel.holoviz.org/reference/panes/PDF.html](https://panel.holoviz.org/reference/panes/PDF.html)

Example:

\>\>\>
PDF(
...
'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf',
...
width=300,
height=410
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [class="reference internal" title="panel.pane.markup.HTMLBasePane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
> [title="panel.pane.image.FileBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](#panel.pane.image.FileBase):
> embed
>
>

`start_page`` ``=`` ``Integer(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start`` ``page')`
Start page of the pdf, by default the first page.

class panel.pane.image.PNG(object=None, **params)
Bases: [ImageBase](#panel.pane.image.ImageBase)

The PNG pane embeds a .png image file in a panel if provided a local
path, or will link to a remote image if provided a URL.

Reference: [https://panel.holoviz.org/reference/panes/PNG.html](https://panel.holoviz.org/reference/panes/PNG.html)

Example:

\>\>\>
PNG(
...
'https://panel.holoviz.org/\_static/logo_horizontal.png',
...
alt_text='The
Panel Logo', ...
link_url='https://panel.holoviz.org/index.html',
...
width=500
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [class="reference internal" title="panel.pane.markup.HTMLBasePane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
> [title="panel.pane.image.FileBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](#panel.pane.image.FileBase):
> embed
>
> [title="panel.pane.image.ImageBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.ImageBase](#panel.pane.image.ImageBase):
> alt_text, caption, fixed_aspect, link_url, target
>
>

class panel.pane.image.SVG(object=None, **params)
Bases: [ImageBase](#panel.pane.image.ImageBase)

The SVG pane embeds a .svg image file in a panel if provided a local
path, or will link to a remote image if provided a URL.

Reference: [https://panel.holoviz.org/reference/panes/SVG.html](https://panel.holoviz.org/reference/panes/SVG.html)

Example:

\>\>\>
SVG(
...
'https://upload.wikimedia.org/wikipedia/commons/6/6b/Bitmap_VS_SVG.svg',
...
alt_text='A
gif vs svg comparison',
...
link_url='https://en.wikipedia.org/wiki/SVG',
...
width=300,
height=400
... )

Methods

|  |  |
|----|----|
| [applies](#panel.pane.image.SVG.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [class="reference internal" title="panel.pane.markup.HTMLBasePane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
> [title="panel.pane.image.FileBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](#panel.pane.image.FileBase):
> embed
>
> [title="panel.pane.image.ImageBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.ImageBase](#panel.pane.image.ImageBase):
> alt_text, caption, fixed_aspect, link_url, target
>
>

`encode`` ``=`` ``Boolean(default=True,`` ``label='Encode')`
Whether to enable base64 encoding of the SVG, base64 encoded SVGs do not
support links.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.image.WebP(object=None, **params)
Bases: [ImageBase](#panel.pane.image.ImageBase)

The WebP pane embeds a .webp image file in a panel if provided a local
path, or will link to a remote image if provided a URL.

Reference: [https://panel.holoviz.org/reference/panes/WebP.html](https://panel.holoviz.org/reference/panes/WebP.html)

Example:

\>\>\>
WebP(
...
'https://assets.holoviz.org/panel/samples/webp_sample.webp',
...
alt_text='A
nice tree', ...
link_url='https://en.wikipedia.org/wiki/WebP',
...
width=500,
...
caption='A
nice tree' ... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [class="reference internal" title="panel.pane.markup.HTMLBasePane"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](panel.pane.markup.md#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
> [title="panel.pane.image.FileBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.FileBase](#panel.pane.image.FileBase):
> embed
>
> [title="panel.pane.image.ImageBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.image.ImageBase](#panel.pane.image.ImageBase):
> alt_text, caption, fixed_aspect, link_url, target
>
>

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
