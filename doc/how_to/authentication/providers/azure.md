## **Azure Entra ID**

Previously known as Azure Active Directory.

To set up OAuth2.0 authentication for Azure Entra ID follow [these instructions](https://docs.microsoft.com/en-us/azure/api-management/api-management-howto-protect-backend-with-aad). Ensure that you supply the tenant ID using `oauth_extra_params`, a configuration may look like:

```bash
panel serve app.py \
--oauth-provider=azure \
--oauth-key='CLIENT_ID' \
--oauth-secret='CLIENT_SECRET' \
--cookie-secret='COOKIE_SECRET' \
--oauth-encryption-key='ENCRYPTION_KEY' \
--oauth-redirect-uri=REDIRECT_URI \
--oauth-extra-params "{'tenant': 'TENANT_ID'}" \
...
```

or with environment variables

```bash
PANEL_OAUTH_PROVIDER=azure \
PANEL_OAUTH_KEY=CLIENT_ID \
PANEL_OAUTH_SECRET=CLIENT_SECRET \
PANEL_COOKIE_SECRET=COOKIE_SECRET \
PANEL_OAUTH_ENCRYPTION=ENCRYPTION_KEY \
PANEL_OAUTH_REDIRECT_URI=REDIRECT_URI \
PANEL_OAUTH_EXTRA_PARAMS="{'tenant': 'TENANT_ID'}" \
panel serve app.py ...
```

The `CLIENT_ID` corresponds to the `Application (client) ID` and the `TENANT_ID` to the `Directory (tenant) ID` below:

![CLIENT_ID and TENANT_ID](../../../_static/images/azure_oauth_app_registration.png)

The `CLIENT_SECRET` corresponds to the `Value` below:

![CLIENT_SECRET](../../../_static/images/azure_oauth_client_secret.png)

The `REDIRECT_URI` should be included in the list of Web Redirect URIs:

![REDIRECT_URI](../../../_static/images/azure_oauth_uris.png)
