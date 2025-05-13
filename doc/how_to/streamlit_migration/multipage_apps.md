# Multi Page Apps

Migrating your Streamlit multi page app to Panel is simple. In Panel each page is simply a file
that you *serve*

```bash
panel serve home.py page1.py page2.ipynb
```

Besides that, a couple of useful flags to further configure a multi-page deployment are:

* `--index`: Set as site index the application page of your preference. For example, to leave
  the *home* application page as index you can pass `--index=home`

  ```bash
  panel serve home.py page1.py page2.ipynb --index=app
  ```

  The `--index` flag also supports a path to a custom Jinja template to be used as index.
  For this template, the following variables will be available:

  * `PANEL_CDN`: URL to the Holoviz Panel CDN.
  * `prefix`: The base URL from where applications are being served.
  * `items`: List of tuples with the application page slug and title to display.

* `--titles`: Set the titles for the application items shown in the default index page as cards.
  By default, the titles shown are the application page slug as a title (without slash and first
  letter upper case). You can use this flag the to, for example, show instead of `Page1` and `Page2`
  different titles like `Page 1` and `Page 2`

  ```bash
  panel serve home.py page1.py page2.ipynb --titles Home "Page 1" "Page 2"
  ```
