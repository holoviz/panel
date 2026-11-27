# Security Policy

## Supported Versions

Security fixes are made in the latest minor release of Panel. When a vulnerability is severe, particularly one that is reachable by a remote client of a default Panel server, we may also backport the fix to the previous minor release, as was done for 1.9.5 and 1.10.1.

| Version | Supported                      |
| ------- | ------------------------------ |
| 1.11.x  | :white_check_mark:             |
| 1.10.x  | :warning: critical fixes only  |
| 1.9.x   | :warning: critical fixes only  |
| < 1.9   | :x:                            |

## Reporting a Vulnerability

Please report suspected vulnerabilities privately using [GitHub's private vulnerability reporting](https://github.com/holoviz/panel/security/advisories/new). Do not open a public issue or pull request for a suspected vulnerability.

A useful report includes:

- The affected Panel version and how Panel is deployed (`panel serve`, ASGI, Jupyter, static export, Pyodide).
- A minimal, runnable reproduction. If it needs application code, show the smallest app that triggers the behavior.
- Which code path is reachable by an untrusted client without the application author writing code that passes untrusted input into a sensitive API.
- The realistic impact.

We aim to acknowledge reports within 7 days and to give a first assessment within 14 days. Panel is maintained by a small team, so these are targets and not guarantees. We will keep you updated on the status of the report until it is resolved.

If a report is accepted, we will develop a fix privately, release it, and publish an advisory crediting the reporter unless they prefer to stay anonymous. If it is declined, we will explain why. Reports that are not accepted may still lead to a regular public hardening change.

## Scope

Panel is a framework for building applications, and many of its APIs deliberately render or load whatever the application author passes in. We treat a report as a vulnerability in Panel when an untrusted client can reach the behavior in a default Panel server, or when documented behavior is violated and the resulting data flow is one an application author would reasonably rely on.

The following are generally not considered vulnerabilities in Panel:

- Applications that pass untrusted input to APIs that are documented to render, load or execute it, such as `pn.pane.HTML`, `pn.pane.Markdown` with raw HTML, `pn.pane.JSON` URLs, file and URL loaders, or `eval`-like parameters. Sanitize such input in your application.
- Behavior that only occurs when building Panel from source or running developer tooling, such as `panel bundle`, `hatch_build.py` or the release scripts, and which does not affect the published packages.
- Findings from automated scanners without a demonstrated path from an untrusted client to the affected code.
- Denial of service that requires an authenticated or otherwise trusted user, or that is only a matter of resource limits you can configure on the server, such as websocket message sizes.
- Custom endpoints, templates and extensions written by application authors, which are not covered by Panel's authentication unless documented otherwise.
- Vulnerabilities in dependencies such as Bokeh, Tornado or FastAPI. Please report those to the respective project.

Panel's authentication and authorization features are in scope. Examples include bypassing `authorize_callback`, `--basic-auth` and OAuth restrictions, and session handling in the server.

## Deploying Panel Securely

Panel servers run application code on behalf of whoever can reach them. For deployments exposed to untrusted users, we recommend enabling [authentication](https://panel.holoviz.org/how_to/authentication/index.html), restricting `--allow-websocket-origin`, running behind a reverse proxy with TLS, and keeping Panel and its dependencies up to date.
