const toctreeDirective = {
  name: 'toctree',
  doc: 'Stub to render Sphinx Toctree directives ',
  arg: { },
  options: {},
  run() {
    return []
  },
};

const plugin = { name: 'Toctree', directives: [toctreeDirective] };

export default plugin;
