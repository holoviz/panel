# Multi Page Apps

Migrating your Streamlit multi page app to Panel is simple. In Panel each page is simply a file
that you *serve*

```bash
panel serve home.py page1.py page2.ipynb
```

You can specify the *home* page with the `--index` flag.

```bash
panel serve home.py page1.py page2.ipynb --index=home
```
