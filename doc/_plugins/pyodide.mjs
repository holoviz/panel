const pyodideDirective = {
  name: 'pyodide',
  doc: 'Stub to render Sphinx Pyodide directives ',
  arg: { },
  options: {},
  run(data) {
    return [{type: 'code', language: 'python', children: [{ type: 'text', 'value': data.node.value}]} ]
  },
};

const plugin = { name: 'Pyodide', directives: [pyodideDirective] };

export default plugin;
