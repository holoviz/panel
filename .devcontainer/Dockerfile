FROM python:3.9.17-bookworm

EXPOSE 5006-5100 8000
ARG CS_VERSION="4.5.1"
ENV DISPLAY ":99.0"
ENV MOZ_HEADLESS 1
ENV MPLBACKEND "Agg"
ENV OMP_NUM_THREADS 1
ENV OPENSSL_CONF=/repos/panel/.devcontainer/openssl.cnf
ENV PANEL_IPYWIDGET 1
ENV PYTHONIOENCODING "utf-8"
ENV SETUPTOOLS_ENABLE_FEATURES "legacy-editable"

WORKDIR /repos/panel/.devcontainer
ADD .devcontainer/openssl.cnf .

# Install nodejs, graphviz etc
RUN curl -fsSL https://deb.nodesource.com/setup_18.x --insecure | bash -
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1-mesa-dev \
        xvfb \
        graphviz-dev \
        nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install and support code server (VS Code)
RUN curl -fOL https://github.com/cdr/code-server/releases/download/v${CS_VERSION}/code-server_${CS_VERSION}_amd64.deb
RUN dpkg -i code-server_${CS_VERSION}_amd64.deb
RUN rm code-server_${CS_VERSION}_amd64.deb

# Dependencies

WORKDIR /repos/panel
ADD . .
RUN pip install -e .[all,build] && \
    pip install pyecharts ipywidgets_bokeh==1.4.0.dev3 && \
    pip install jupyterlab jupyter-server-proxy jupyter-vscode-proxy jedi-language-server jupyterlab-git rope jupyter-bokeh sphinx-autobuild
RUN echo '' >> panel/template/base.py
RUN echo 'BasicTemplate.param.site_url.default="./"' >> panel/template/base.py

# Build Docs
RUN bokeh sampledata
RUN python ./doc/generate_modules.py panel -d ./doc/api -n panel -e tests
RUN python scripts/gallery/convert_gallery.py
RUN nbsite build --what=html --output=builtdocs --org holoviz --project-name panel

ENTRYPOINT ["source", ".devcontainer/start.sh"]