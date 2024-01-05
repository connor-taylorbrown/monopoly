# Example project

## Setup guide

### JSON Server
Reference: https://www.npmjs.com/package/json-server
1. `npm update -g npm`: Update npm to latest version.
1. `npm install -g json-server`: Install json-server host tool globally.
1. `json-server --watch json/quotes.json`: Serve `json/quotes.json`, watching file for changes.

Proceed from step 3 (Serve JSON) when json-server is already installed.

### Tailwind
Reference: https://tailwindcss.com/docs/installation
1. `npm install -D tailwindcss`: Add tailwindcss as a dev dependency.
1. `npx tailwindcss init`: Create tailwind.config.js
1. `npx tailwindcss -i ./input.css -o ./static/css/main.css --watch`: Generate stylesheets (use `--watch` to monitor changes to templates and update `main.css` accordingly)

Proceed from step 3 (Generate stylesheets) on existing projects where the necessary config files have already been created.

### HTMX
Reference: https://htmx.org

No set up required for now. Future work may involve vendoring the HTMX dependency.

### Flask
Reference: https://flask-htmx.readthedocs.io/en/latest/quickstart.html
1. `python3 -m venv venv`: Create new virtual environment at relative path `venv`. Replace `python3` with the relevant command on your system, i.e. `py` or `python`.
1. Enter your newly created virtual environment: VS Code should detect this for you and enter `venv` after restarting terminal. To do this manually, run the following:
```source venv/bin/activate```
1. `pip install -r requirements.txt`: Install packages required to run application.
1. `flask run --debug`: Launch the application in debug mode.
    - Substitute with `gunicorn --bind :8080 app:app` to test production configuration.

Proceed from step 4 (Launch application) if dependencies have already been installed.

## Project structure
This repository is arranged to support running Flask with default configuration. Flask makes use of the following directories:
- `static`: used for serving static content, such as CSS stylesheets.
- `templates`: used for sourcing templates named in `render_template` calls.
