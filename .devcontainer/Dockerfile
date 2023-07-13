FROM python:3.9.17-bookworm

ARG CS_VERSION="4.5.1"

# Install and support code server (VS Code)
RUN curl -fOL https://github.com/cdr/code-server/releases/download/v${CS_VERSION}/code-server_${CS_VERSION}_amd64.deb
RUN dpkg -i code-server_${CS_VERSION}_amd64.deb
RUN rm code-server_${CS_VERSION}_amd64.deb

WORKDIR /repos
RUN git clone https://github.com/holoviz/panel.git
WORKDIR /repos/panel
RUN pip install -e .[tests,recommmended,doc]
RUN pip install jupyterlab jupyter-server-proxy jupyter-vscode-proxy jedi-language-server

# Docs
RUN bokeh sampledata
RUN python ./doc/generate_modules.py panel -d ./doc/api -n panel -e tests
RUN python scripts/gallery/convert_gallery.py
# RUN nbsite build --what=html --output=builtdocs --org holoviz --project-name panel
# RUN cp -r ./panel/dist ./builtdocs/panel_dist

ENTRYPOINT ["/bin/bash"]
# RUN pre-commit install
#   - jupyter-server-proxy
#   - jupyterlab-git
#   - jupyter_conda
#   - nb_conda_kernels
#   - jupyter-vscode-proxy
#   - jedi-language-server
#   - rope
#   - jupyter-bokeh


