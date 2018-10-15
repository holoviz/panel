"""
Commandline interface to Panel
"""

import ast
import sys
import tempfile
from bokeh.__main__ import main as bokeh_entry_point


try:
    import nbformat
except:
    nbformat = None

try:
    import nbconvert
except:
    nbconvert = None


def comment_out_magics(source):
    """
    Utility used to make sure AST parser does not choke on unrecognized
    magics.
    """
    filtered = []
    for line in source.splitlines():
        if line.strip().startswith('%'):
            filtered.append('# ' +  line)
        else:
            filtered.append(line)
    return '\n'.join(filtered)


def wrap_cell_expression(source, template='{expr}'):
    """
    If a cell ends in an expression that could be displaying a HoloViews
    object (as determined using the AST), wrap it with a given prefix
    and suffix string.

    If the cell doesn't end in an expression, return the source unchanged.
    """
    cell_output_types = (ast.IfExp, ast.BoolOp, ast.BinOp, ast.Call,
                         ast.Name, ast.Attribute)
    try:
        node = ast.parse(comment_out_magics(source))
    except SyntaxError:
        return source
    filtered = source.splitlines()
    if node.body != []:
        last_expr = node.body[-1]
        if not isinstance(last_expr, ast.Expr):
            pass # Not an expression
        elif isinstance(last_expr.value, cell_output_types):
            # CAREFUL WITH UTF8!
            expr_end_slice = filtered[last_expr.lineno-1][:last_expr.col_offset]
            expr_start_slice = filtered[last_expr.lineno-1][last_expr.col_offset:]
            start = '\n'.join(filtered[:last_expr.lineno-1]
                              + ([expr_end_slice] if expr_end_slice else []))
            ending = '\n'.join(([expr_start_slice] if expr_start_slice else [])
                            + filtered[last_expr.lineno:])
            # BUG!! Adds newline for 'foo'; <expr>
            return start + '\n' + template.format(expr=ending)
    return source



class PanelProcessor(nbconvert.preprocessors.Preprocessor):
    """
    Preprocessor to convert notebooks to Python source to convert use of
    opts magic to use the util.opts utility instead.
    """

    def preprocess_cell(self, cell, resources, index):
        if cell['cell_type'] == 'code':
            template = 'import panel;panel.serve_panel({expr})'
            source = wrap_cell_expression(cell['source'], template)
            cell['source'] = source

        if cell['cell_type'] == 'markdown':
            lines = len(cell['source'].splitlines())
            source = "source='''{source}'''".format(source=cell['source'])
            cell['source'] = '\n'.join([source,
                                        'import panel;panel.serve_markdown(source, {lines})'.format(lines=lines)])
            cell['cell_type'] = 'code'
            cell['outputs'] = []
            cell['execution_count'] = 0

        return cell, resources

    def __call__(self, nb, resources): return self.preprocess(nb,resources)



class StripMagicsProcessor(nbconvert.preprocessors.Preprocessor):
    """
    Preprocessor to convert notebooks to Python source to strips out all
    magics. To be applied after the preprocessors that can handle
    specific magics appropriately.
    """

    def strip_magics(self, source):
        """
        Given the source of a cell, filter out all cell and line magics.
        """
        filtered=[]
        for line in source.splitlines():
            if not line.startswith('%') or line.startswith('%%'):
                filtered.append(line)
        return '\n'.join(filtered)


    def preprocess_cell(self, cell, resources, index):
        if cell['cell_type'] == 'code':
            cell['source'] = self.strip_magics(cell['source'])
        return cell, resources

    def __call__(self, nb, resources): return self.preprocess(nb,resources)


def export_to_python(filename=None,
                     preprocessors=[PanelProcessor(),
                                    StripMagicsProcessor()]):

    filename = filename if filename else sys.argv[1]
    with open(filename) as f:
        nb = nbformat.read(f, nbformat.NO_CONVERT)
        exporter = nbconvert.PythonExporter()
        for preprocessor in preprocessors:
            exporter.register_preprocessor(preprocessor)
        source, meta = exporter.from_notebook_node(nb)
        return source


def main():
    if 'report' == sys.argv[1]:
        if None in [nbconvert, nbformat]:
            raise Exception('nbconvert and nbformat dependencies not satisfied')
        notebook = sys.argv[2]
        cmd_replacement = []
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            f.write(export_to_python(notebook).encode('utf8'))
            cmd_replacement = ['serve', f.name]
        sys.argv = sys.argv[:1] + cmd_replacement + sys.argv[3:]
        bokeh_entry_point()
    else:
        bokeh_entry_point()
