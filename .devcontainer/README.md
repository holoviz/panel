## Build Locally

docker build -f .devcontainer/Dockerfile -t panel_dev:latest .

## Run

docker run --publish 8888:8888 -it panel_dev:latest

Open

- lab: http://127.0.0.1:8888/lab
- VS CODE: http://127.0.0.1:8888/vscode
