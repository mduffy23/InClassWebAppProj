# Lab Shop: Flask security workshop starter app

Lab Shop is a small Flask app that is **intentionally insecure**. You will scan it, attack it, and fix it. This should be a good example for your final project.

## Rules of engagement

- Run this app **only on your own computer** (it binds to `127.0.0.1`). Never deploy it, host it publicly, or change it to listen on a network address.
- Your only authorized targets are this app on your machine and your own partner's copy if you are working as a pair.
- Do not scan or attack campus systems, other students' machines, or any website or service.
- Do not copy code from this app into real projects. It contains mistakes on purpose.
- If a tool shows you something unexpected, stop and tell the instructor.

## Setup - Run this in the project folder `InClassWebAppProj`

You need Python 3.10 or newer. On macOS and Linux, use `python3` and `pip3` in the commands below if `python` or `pip` is not found.

```bash
python -m venv .venv

# The above command may activate the env, but if it does not (or you are not sure) run this just in case
## macOS / Linux
source .venv/bin/activate
## Windows (PowerShell)
.venv\Scripts\Activate.ps1

# This will take a moment
pip install -r requirements-dev.txt

# This will start up the app
python app.py
```

Open http://127.0.0.1:5000 in your browser. You should see the Lab Shop home page.

To start over with fresh data, stop the app and delete the `lab.db` file.

Semgrep can be difficult to install on native Windows. If it fails, use Bandit (it covers much of the same ground for this lab) or work in WSL, and tell the instructor. Wapiti or [ZAP](https://www.zaproxy.org/download/) can make up the ground as well.

## Test account

| Username | Password |
|---|---|
| alice | password1 |

Log in as alice to see what a normal customer sees. Finding out what else is in the app is part of the lab.

## Lab commands

Run these from the project folder with your virtual environment active.

```bash
# 1. Static analysis of the source code
## For semgrep, you are asking for rulesets!
semgrep --config p/flask --config p/owasp-top-ten .
bandit -r app.py

# 2. Known-vulnerable dependencies
pip-audit -r requirements.txt

# 3. Optional, scan live app
##    In ZAP: Quick Start > Automated Scan > http://127.0.0.1:5000
##    Use Wapiti
### Not in the .venv, install Wapiti and have it scan the running app
pip install wapiti3
wapiti -u http://127.0.0.1:5000/ -f html -o wapiti-report
```

## Triage table

For each finding, record:

| Tool | Finding | Real or false positive? | Severity | Fix | Policy or control it relates to |
|---|---|---|---|---|---|

Fix at least two findings, rerun the tools, and confirm the findings are gone.

Is there anything the tools missed in your view?

## For your own project

Run the same tools on your own app and include before-and-after results in your submission, along with a short note on what each tool found and what it missed.