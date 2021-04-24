"""This setup.py will install a package that configures the jupyter-server-proxy to
panel serve the example notebooks."""
import setuptools

setuptools.setup(
    name="jupyter-voila-docs-server",
    py_modules=["jupyter_voila_docs_server"],
    entry_points={
        "jupyter_serverproxy_servers": [
            "docs = jupyter_voila_docs_server:voila_serve_examples",
        ]
    },
    install_requires=["jupyter-server-proxy", "voila"],
)
