# Configuring Authentication

Authentication is a difficult topic fraught with potential pitfalls and complicated configuration options. Panel aims to be a "batteries-included" package for building applications and dashboards and therefore ships with a number of built-in providers for authentication in an application.

The primary mechanism by which Panel performs authentication is [OAuth 2.0](https://oauth.net/2/). The official specification for OAuth 2.0 describes the protocol as follows:

    The OAuth 2.0 authorization framework enables a third-party
    application to obtain limited access to an HTTP service, either on
    behalf of a resource owner by orchestrating an approval interaction
    between the resource owner and the HTTP service, or by allowing the
    third-party application to obtain access on its own behalf.

In other words, OAuth delegates authentication to a third-party provider, such as GitHub, Google, or Azure Entra ID, to authenticate user credentials and grant limited access to the APIs of that service.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`unlock;2.5em;sd-mr-1 sd-animate-grow50` Configuring Basic Authentication
:link: basic
:link-type: doc

Discover how to add basic password-based authentication to your application.
:::

:::{grid-item-card} {octicon}`gear;2.5em;sd-mr-1 sd-animate-grow50` Configuring OAuth
:link: configuration
:link-type: doc

Discover how to configure OAuth from the command line.
:::

:::{grid-item-card} {octicon}`unlock;2.5em;sd-mr-1 sd-animate-grow50` Configuring PAM Authentication
:link: pam
:link-type: doc

Discover how to configure Panel apps to authenticate against your system credentials (using PAM).
:::

:::{grid-item-card} {octicon}`shield;2.5em;sd-mr-1 sd-animate-grow50` OAuth Providers
:link: providers/index
:link-type: doc

A list of OAuth providers and how to configure them.
:::

:::{grid-item-card} {octicon}`file;2.5em;sd-mr-1 sd-animate-grow50` Templates
:link: templates
:link-type: doc

Discover how to configure error and logout templates to match the design of your application.
:::

:::{grid-item-card} {octicon}`person;2.5em;sd-mr-1 sd-animate-grow50` User Information
:link: user_info
:link-type: doc

Discover how to access and use the user information provided by your OAuth provider.
:::


:::{grid-item-card} {octicon}`file-badge;2.5em;sd-mr-1 sd-animate-grow50` Access Tokens
:link: access_tokens
:link-type: doc

Discover how to use OAuth access tokens and ensure they are automatically refreshed when they expire.
:::

:::{grid-item-card} {octicon}`verified;2.5em;sd-mr-1 sd-animate-grow50` Authorization Callbacks
:link: authorization
:link-type: doc

Discover how to configure a callback to implement custom authorization logic.
:::

:::{grid-item-card} {octicon}`person-fill;2.5em;sd-mr-1 sd-animate-grow50` Optional Authentication
:link: guest_users
:link-type: doc

Discover how to allow guest users to access specific endpoints or the entire application.
:::

:::{grid-item-card} {octicon}`bug-fill;2.5em;sd-mr-1 sd-animate-grow50` Troubleshooting
:link: trouble_shooting
:link-type: doc

Discover solutions for common OAuth configuration and connection issues.
:::

::::

Note that since Panel is built on Bokeh server and Tornado, it is also possible to implement your own authentication independent of the OAuth components shipped with Panel. [See the Bokeh documentation](https://docs.bokeh.org/en/latest/docs/user_guide/server.html#authentication) for further information.

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

basic
configuration
pam
providers/index
templates
user_info
access_tokens
authorization
guest_users
trouble_shooting
```
