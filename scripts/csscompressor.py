"""
Portions Copyright (c) 2013 Sprymix Inc.
Portions Copyright (c) 2011-2013, Yahoo! Inc.

Original YUI-Compressor LICENSE
===============================

All rights reserved.

Redistribution and use of this software in source and binary forms,
with or without modification, are permitted provided that the following
conditions are met:

* Redistributions of source code must retain the above
  copyright notice, this list of conditions and the
  following disclaimer.

* Redistributions in binary form must reproduce the above
  copyright notice, this list of conditions and the
  following disclaimer in the documentation and/or other
  materials provided with the distribution.

* Neither the name of Yahoo! Inc. nor the names of its
  contributors may be used to endorse or promote products
  derived from this software without specific prior
  written permission of Yahoo! Inc.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Portions Copyright (c) 2013 Sprymix Inc.
# Author of python port: Yury Selivanov - http://sprymix.com
#
# Author: Julien Lecomte -  http://www.julienlecomte.net/
# Author: Isaac Schlueter - http://foohack.com/
# Author: Stoyan Stefanov - http://phpied.com/
# Contributor: Dan Beam - http://danbeam.org/
# Contributor: w.Tayyeb - http://tayyeb.info/
# Portions Copyright (c) 2011-2013 Yahoo! Inc.  All rights reserved.
# LICENSE: BSD (revised)
"""

__all__ = ('compress', 'compress_partitioned')
__version__ = '0.9.4'


import re

_url_re = re.compile(r'''(url)\s*\(\s*(['"]?)data\:''', re.I)
_calc_re = re.compile(r'(calc)\s*\(', re.I)
_hsl_re = re.compile(r'(hsl|hsla)\s*\(', re.I)
_ws_re = re.compile(r'\s+')
_str_re = re.compile(r'''("([^\\"]|\\.|\\)*")|('([^\\']|\\.|\\)*')''')
_yui_comment_re = re.compile(r'___YUICSSMIN_PRESERVE_CANDIDATE_COMMENT_(?P<num>\d+)___')
_ms_filter_re = re.compile(r'progid\:DXImageTransform\.Microsoft\.Alpha\(Opacity=', re.I)
_spaces1_re = re.compile(r'(^|\})(([^\{:])+:)+([^\{]*\{)')
_spaces2_re = re.compile(r'\s+([!{};:>+\(\)\],])')
_ie6special_re = re.compile(r':first-(line|letter)(\{|,)', re.I)
_charset1_re = re.compile(r'^(.*)(@charset)\s+("[^"]*";)', re.I)
_charset2_re = re.compile(r'^((\s*)(@charset)\s+([^;]+;\s*))+', re.I)
_dirs_re = re.compile(r'''@(font-face|import|
                            (?:-(?:atsc|khtml|moz|ms|o|wap|webkit)-)?
                                            keyframe|media|page|namespace)''',
                      re.I | re.X)

_pseudo_re = re.compile(r''':(active|after|before|checked|disabled|empty|enabled|
                                    first-(?:child|of-type)|focus|hover|last-(?:child|of-type)|
                                    link|only-(?:child|of-type)|root|:selection|target|visited)''',
                        re.I | re.X)

_common_funcs_re = re.compile(r''':(lang|not|nth-child|nth-last-child|nth-last-of-type|
                                        nth-of-type|(?:-(?:moz|webkit)-)?any)\(''', re.I | re.X)

_common_val_funcs_re = re.compile(r'''([:,\(\s]\s*)(attr|color-stop|from|rgba|to|url|
                                        (?:-(?:atsc|khtml|moz|ms|o|wap|webkit)-)?
                                        (?:calc|max|min|(?:repeating-)?
                                            (?:linear|radial)-gradient)|-webkit-gradient)''',
                                  re.I | re.X)

_space_and_re = re.compile(r'\band\(', re.I)

_space_after_re = re.compile(r'([!{}:;>+\(\[,])\s+')

_semi_re = re.compile(r';+}')

_zero_fmt_spec_re = re.compile(r'''(\s|:|\(|,)(?:0?\.)?0
                                    (?:px|em|%|in|cm|mm|pc|pt|ex|deg|g?rad|k?hz)''',
                               re.I | re.X)

_zero_req_unit_re = re.compile(r'''(\s|:|\(|,)(?:0?\.)?0
                                    (m?s)''', re.I | re.X)

_bg_pos_re = re.compile(r'''(background-position|webkit-mask-position|transform-origin|
                                webkit-transform-origin|moz-transform-origin|o-transform-origin|
                                ms-transform-origin):0(;|})''', re.I | re.X)

_quad_0_re = re.compile(r':0 0 0 0(;|})')
_trip_0_re = re.compile(r':0 0 0(;|})')
_coup_0_re = re.compile(r':0 0(;|})')

_point_float_re = re.compile(r'(:|\s)0+\.(\d+)')
_point_float_neg_re = re.compile(r'(:|\s)-0+\.(\d+)')
_point_float_pos_re = re.compile(r'(:|\s)\+(\d+)+\.(\d+)')

_border_re = re.compile(r'''(border|border-top|border-right|border-bottom|
                                border-left|outline|background):none(;|})''', re.I | re.X)

_o_px_ratio_re = re.compile(r'\(([\-A-Za-z]+):([0-9]+)\/([0-9]+)\)')

_empty_rules_re = re.compile(r'[^\}\{/;]+\{\}')

_many_semi_re = re.compile(';;+')

_rgb_re = re.compile(r'rgb\s*\(\s*([0-9,\s]+)\s*\)')

_hex_color_re = re.compile(r'''(\=\s*?["']?)?
                                   \#([0-9a-fA-F])([0-9a-fA-F])
                                     ([0-9a-fA-F])([0-9a-fA-F])
                                     ([0-9a-fA-F])([0-9a-fA-F])
                               (\}|[^0-9a-fA-F{][^{]*?\})''', re.X)

_ie_matrix_re = re.compile(r'\s*filter:\s*progid:DXImageTransform\.Microsoft\.Matrix\(([^\)]+)\);')

_colors_map = {
    'f00':     'red',
    '000080':  'navy',
    '808080':  'gray',
    '808000':  'olive',
    '800080':  'purple',
    'c0c0c0':  'silver',
    '008080':  'teal',
    'ffa500':  'orange',
    '800000':  'maroon'
}

_colors_re = re.compile(r'(:|\s)' + '(\\#(' + '|'.join(_colors_map.keys()) + '))' + r'(;|})', re.I)


def _preserve_call_tokens(css, regexp, preserved_tokens, remove_ws=False):
    max_idx = len(css) - 1
    append_idx = 0
    sb = []
    nest_term = None

    for match in regexp.finditer(css):
        name = match.group(1)
        start_idx = match.start(0) + len(name) + 1 # "len" of "url("

        term = match.group(2) if match.lastindex > 1 else None
        if not term:
            term = ')'
            nest_term = '('

        found_term = False
        end_idx = match.end(0) - 1
        nest_idx = end_idx if nest_term else 0
        nested = False
        while not found_term and (end_idx + 1) <= max_idx:
            if nest_term:
                nest_idx = css.find(nest_term, nest_idx + 1)
            end_idx = css.find(term, end_idx + 1)

            if end_idx > 0:
                if nest_idx > 0 and nest_idx < end_idx and \
                                css[nest_idx - 1] != '\\':
                    nested = True

                if css[end_idx - 1] != '\\':
                    if nested:
                        nested = False
                    else:
                        found_term = True
                        if term != ')':
                            end_idx = css.find(')', end_idx)
            else:
                raise ValueError('malformed css')

        sb.append(css[append_idx:match.start(0)])

        assert found_term

        token = css[start_idx:end_idx].strip()

        if remove_ws:
            token = _ws_re.sub('', token)

        preserver = ('{0}(___YUICSSMIN_PRESERVED_TOKEN_{1}___)'
                                .format(name, len(preserved_tokens)))

        preserved_tokens.append(token)
        sb.append(preserver)

        append_idx = end_idx + 1

    sb.append(css[append_idx:])

    return ''.join(sb)


def _compress_rgb_calls(css):
    # Shorten colors from rgb(51,102,153) to #336699
    # This makes it more likely that it'll get further compressed in the next step.
    def _replace(match):
        rgb_colors = match.group(1).split(',')
        result = '#'
        for comp in rgb_colors:
            comp = int(comp)
            if comp < 16:
                result += '0'
            if comp > 255:
                comp = 255
            result += hex(comp)[2:].lower()
        return result
    return _rgb_re.sub(_replace, css)


def _compress_hex_colors(css):
    # Shorten colors from #AABBCC to #ABC. Note that we want to make sure
    # the color is not preceded by either ", " or =. Indeed, the property
    #     filter: chroma(color="#FFFFFF");
    # would become
    #     filter: chroma(color="#FFF");
    # which makes the filter break in IE.
    # We also want to make sure we're only compressing #AABBCC patterns inside { },
    # not id selectors ( #FAABAC {} )
    # We also want to avoid compressing invalid values (e.g. #AABBCCD to #ABCD)

    buf = []

    index = 0
    while True:
        match = _hex_color_re.search(css, index)
        if not match:
            break

        buf.append(css[index:match.start(0)])


        if match.group(1):
            # Restore, as is. Compression will break filters
            buf.append(match.group(1) + ('#' + match.group(2) + match.group(3) + match.group(4) +
                                               match.group(5) + match.group(6) + match.group(7)))

        else:
            if (match.group(2).lower() == match.group(3).lower() and
                match.group(4).lower() == match.group(5).lower() and
                match.group(6).lower() == match.group(7).lower()):

                buf.append('#' + (match.group(2) + match.group(4) + match.group(6)).lower())

            else:
                buf.append('#' + (match.group(2) + match.group(3) + match.group(4) +
                                  match.group(5) + match.group(6) + match.group(7)).lower())

        index = match.end(7)

    buf.append(css[index:])

    return ''.join(buf)


def _compress(css, max_linelen=0, preserve_exclamation_comments=True):
    start_idx = end_idx = 0
    total_len = len(css)

    preserved_tokens = []
    css = _preserve_call_tokens(css, _url_re, preserved_tokens, remove_ws=True)
    css = _preserve_call_tokens(css, _calc_re, preserved_tokens, remove_ws=False)
    css = _preserve_call_tokens(css, _hsl_re, preserved_tokens, remove_ws=True)

    # Collect all comments blocks...
    comments = []
    while True:
        start_idx = css.find('/*', start_idx)
        if start_idx < 0:
            break

        suffix = ''
        end_idx = css.find('*/', start_idx + 2)
        if end_idx < 0:
            end_idx = total_len
            suffix = '*/'

        token = css[start_idx + 2:end_idx]
        comments.append(token)

        css = (css[:start_idx + 2] +
               '___YUICSSMIN_PRESERVE_CANDIDATE_COMMENT_{0}___'.format(len(comments)-1) +
               css[end_idx:] + suffix)

        start_idx += 2

    # preserve strings so their content doesn't get accidentally minified
    def _replace(match):
        token = match.group(0)
        quote = token[0]
        token = token[1:-1]


        # maybe the string contains a comment-like substring?
        # one, maybe more? put'em back then
        if '___YUICSSMIN_PRESERVE_CANDIDATE_COMMENT_' in token:
            token = _yui_comment_re.sub(lambda match: comments[int(match.group('num'))], token)

        token = _ms_filter_re.sub('alpha(opacity=', token)

        preserved_tokens.append(token)
        return (quote +
                '___YUICSSMIN_PRESERVED_TOKEN_{0}___'.format(len(preserved_tokens)-1) +
                quote)

    css = _str_re.sub(_replace, css)

    # strings are safe, now wrestle the comments
    comments_iter = iter(comments)
    for i, token in enumerate(comments_iter):
        placeholder = "___YUICSSMIN_PRESERVE_CANDIDATE_COMMENT_{0}___".format(i)

        # ! in the first position of the comment means preserve
        # so push to the preserved tokens while stripping the !
        if preserve_exclamation_comments and token.startswith('!'):
            preserved_tokens.append(token)
            css = css.replace(placeholder, '___YUICSSMIN_PRESERVED_TOKEN_{0}___'.
                              format(len(preserved_tokens)-1))
            continue

        # \ in the last position looks like hack for Mac/IE5
        # shorten that to /*\*/ and the next one to /**/
        if token.endswith('\\'):
            preserved_tokens.append('\\')
            css = css.replace(placeholder,
                              '___YUICSSMIN_PRESERVED_TOKEN_{0}___'.format(len(preserved_tokens)-1))

            # attn: advancing the loop
            next(comments_iter)

            preserved_tokens.append('')
            css = css.replace('___YUICSSMIN_PRESERVE_CANDIDATE_COMMENT_{0}___'.format(i+1),
                              '___YUICSSMIN_PRESERVED_TOKEN_{0}___'.format(len(preserved_tokens)-1))

            continue

        # keep empty comments after child selectors (IE7 hack)
        # e.g. html >/**/ body
        if not token:
            start_idx = css.find(placeholder)
            if start_idx > 2:
                if css[start_idx-3] == '>':
                    preserved_tokens.append('')
                    css = css.replace(placeholder,
                                      '___YUICSSMIN_PRESERVED_TOKEN_{0}___'.
                                      format(len(preserved_tokens)-1))

        # in all other cases kill the comment
        css = css.replace('/*{0}*/'.format(placeholder), '')

    # Normalize all whitespace strings to single spaces. Easier to work with that way.
    css = _ws_re.sub(' ', css)

    def _replace(match):
        token = match.group(1)
        preserved_tokens.append(token);
        return ('filter:progid:DXImageTransform.Microsoft.Matrix(' +
                '___YUICSSMIN_PRESERVED_TOKEN_{0}___);'.format(len(preserved_tokens)-1))
    css = _ie_matrix_re.sub(_replace, css)

    # remove + sign where it is before a float +0.1 +2.34 
    css = _point_float_pos_re.sub(r'\1\2.\3', css)

    # Remove the spaces before the things that should not have spaces before them.
    # But, be careful not to turn "p :link {...}" into "p:link{...}"
    # Swap out any pseudo-class colons with the token, and then swap back.
    css = _spaces1_re.sub(lambda match: match.group(0) \
                                            .replace(':', '___YUICSSMIN_PSEUDOCLASSCOLON___'), css)

    css = _spaces2_re.sub(lambda match: match.group(1), css)

    # Restore spaces for !important
    css = css.replace('!important', ' !important');

    # bring back the colon
    css = css.replace('___YUICSSMIN_PSEUDOCLASSCOLON___', ':')

    # retain space for special IE6 cases
    css = _ie6special_re.sub(
                lambda match: ':first-{0} {1}'.format(match.group(1).lower(), match.group(2)),
                css)

    # no space after the end of a preserved comment
    css = css.replace('*/ ', '*/')

    # If there are multiple @charset directives, push them to the top of the file.
    css = _charset1_re.sub(lambda match: match.group(2).lower() + \
                                         ' ' + match.group(3) + match.group(1),
                           css)

    # When all @charset are at the top, remove the second and after (as they are completely ignored)
    css = _charset2_re.sub(lambda match: match.group(2) + \
                                         match.group(3).lower() + ' ' + match.group(4),
                           css)

    # lowercase some popular @directives (@charset is done right above)
    css = _dirs_re.sub(lambda match: '@' + match.group(1).lower(), css)

    # lowercase some more common pseudo-elements
    css = _pseudo_re.sub(lambda match: ':' + match.group(1).lower(), css)

    # lowercase some more common functions
    css = _common_funcs_re.sub(lambda match: ':' + match.group(1).lower() + '(', css)

    # lower case some common function that can be values
    # NOTE: rgb() isn't useful as we replace with #hex later, as well as and()
    # is already done for us right after this
    css = _common_val_funcs_re.sub(lambda match: match.group(1) + match.group(2).lower(), css)

    # Put the space back in some cases, to support stuff like
    # @media screen and (-webkit-min-device-pixel-ratio:0){
    css = _space_and_re.sub('and (', css)

    # Remove the spaces after the things that should not have spaces after them.
    css = _space_after_re.sub(r'\1', css)

    # remove unnecessary semicolons
    css = _semi_re.sub('}', css)

    # Replace 0(px,em,%) with 0.
    css = _zero_fmt_spec_re.sub(lambda match: match.group(1) + '0', css)

    # Replace 0.0(m,ms) or .0(m,ms) with 0(m,ms)
    css = _zero_req_unit_re.sub(lambda match: match.group(1) + '0' + match.group(2), css)

    # Replace 0 0 0 0; with 0.
    css = _quad_0_re.sub(r':0\1', css)
    css = _trip_0_re.sub(r':0\1', css)
    css = _coup_0_re.sub(r':0\1', css)

    # Replace background-position:0; with background-position:0 0;
    # same for transform-origin
    css = _bg_pos_re.sub(lambda match: match.group(1).lower() + ':0 0' + match.group(2), css)

    # Replace 0.6 to .6, but only when preceded by : or a white-space
    css = _point_float_re.sub(r'\1.\2', css)
    # Replace -0.6 to -.6, but only when preceded by : or a white-space
    css = _point_float_neg_re.sub(r'\1-.\2', css)

    css = _compress_rgb_calls(css)
    css = _compress_hex_colors(css)

    # Replace #f00 -> red; other short color keywords
    css = _colors_re.sub(lambda match: match.group(1) + _colors_map[match.group(3).lower()] +
                                       match.group(4),
                         css)

    # border: none -> border:0
    css = _border_re.sub(lambda match: match.group(1).lower() + ':0' + match.group(2), css)

    # shorter opacity IE filter
    css = _ms_filter_re.sub('alpha(opacity=', css)

    # Find a fraction that is used for Opera's -o-device-pixel-ratio query
    # Add token to add the "\" back in later
    css = _o_px_ratio_re.sub(r'\1:\2___YUI_QUERY_FRACTION___\3', css)

    # Remove empty rules.
    css = _empty_rules_re.sub('', css)

    # Add "\" back to fix Opera -o-device-pixel-ratio query
    css = css.replace('___YUI_QUERY_FRACTION___', '/')

    if max_linelen and len(css) > max_linelen:
        buf = []
        start_pos = 0
        while True:
            buf.append(css[start_pos:start_pos + max_linelen])
            start_pos += max_linelen
            while start_pos < len(css):
                if css[start_pos] == '}':
                    buf.append('}\n')
                    start_pos += 1
                    break
                else:
                    buf.append(css[start_pos])
                    start_pos += 1
            if start_pos >= len(css):
                break
        css = ''.join(buf)

    # Replace multiple semi-colons in a row by a single one
    # See SF bug #1980989
    css = _many_semi_re.sub(';', css)

    return css, preserved_tokens


def _apply_preserved(css, preserved_tokens):
    # restore preserved comments and strings
    for i, token in reversed(tuple(enumerate(preserved_tokens))):
        css = css.replace('___YUICSSMIN_PRESERVED_TOKEN_{0}___'.format(i), token)

    css = css.strip()
    return css


def compress(css, max_linelen=0, preserve_exclamation_comments=True):
    """Compress given CSS stylesheet.

    Parameters:

    - css : str
        An str with CSS rules.

    - max_linelen : int = 0
        Some source control tools don't like it when files containing lines longer
        than, say 8000 characters, are checked in. This option is used in
        that case to split long lines after a specific column.

    - preserve_exclamation_comments : boolean = True
        Some stylesheets contain /*! ... */ comment block which used for copyright
        notices or else. By default compress dont remove them like other comment
        blocks. It will lead to bigger file size. but once you decide to remove
        them just set this parameter to False.

    Returns a ``str`` object with compressed CSS.
    """

    css, preserved_tokens = _compress(css, max_linelen=max_linelen, preserve_exclamation_comments=preserve_exclamation_comments)
    css = _apply_preserved(css, preserved_tokens)
    return css


def compress_partitioned(css,
                         max_linelen=0,
                         max_rules_per_file=4000,
                         preserve_exclamation_comments=True):
    """Compress given CSS stylesheet into a set of files.

    Parameters:

    - max_linelen : int = 0
        Has the same meaning as for "compress()" function.

    - max_rules_per_file : int = 0
        Internet Explorers <= 9 have an artificial max number of rules per CSS
        file (4096; http://blogs.msdn.com/b/ieinternals/archive/2011/05/14/10164546.aspx)
        When ``max_rules_per_file`` is a positive number, the function *always* returns
        a list of ``str`` objects, each limited to contain less than the passed number
        of rules.

	- preserve_exclamation_comments : boolean = True
		Has the same meaning as for "compress()" function.


    Always returns a ``list`` of ``str`` objects with compressed CSS.
    """

    assert max_rules_per_file > 0

    css, preserved_tokens = _compress(css, max_linelen=max_linelen, preserve_exclamation_comments=preserve_exclamation_comments)
    css = css.strip()

    bufs = []
    buf = []
    rules = 0
    while css:
        if rules >= max_rules_per_file:
            bufs.append(''.join(buf))
            rules = 0
            buf = []

        nested = 0
        while True:
            op_idx = css.find('{')
            cl_idx = css.find('}')

            if cl_idx < 0:
                raise ValueError('malformed CSS: non-balanced curly-braces')

            if op_idx < 0 or cl_idx < op_idx: # ... } ... { ...
                nested -= 1

                if nested < 0:
                    raise ValueError('malformed CSS: non-balanced curly-braces')

                buf.append(css[:cl_idx+1])
                css = css[cl_idx+1:]

                if not nested: # closing rules
                    break

            else: # ... { ... } ...
                nested += 1

                rule_line = css[:op_idx+1]
                buf.append(rule_line)
                css = css[op_idx+1:]

                rules += rule_line.count(',') + 1

    bufs.append(''.join(buf))

    bufs = [_apply_preserved(buf, preserved_tokens) for buf in bufs]

    return bufs
