import os
from utils import runtime_helpers

# App config
SECS_PER_WEEK = 60 * 60 * 24 * 7

# Enable ctypes -> Jinja2 tracebacks
DEV_ENV = os.environ.get("SERVER_SOFTWARE", "Development").startswith("Development")

ROOT_DIRECTORY = os.path.dirname(__file__)


# General info
AUTHOR_NAME = "Fenris Lycaon"
SITENAME = "Tyr"
EMAIL_PREFIX = "[ Tyr ] "
TAGLINE = "A personal dashboard to focus on what matters"

# Emails
APP_OWNER = "thefenrislycaon@gmail.com"
ADMIN_EMAIL = APP_OWNER
DAILY_REPORT_RECIPS = [APP_OWNER]
SENDER_EMAIL = APP_OWNER
NOTIF_EMAILS = [APP_OWNER]

GCS_REPORT_BUCKET = "/tyr_reports"
BACKGROUND_SERVICE = "default"

COOKIE_NAME = "tyr_session"



try:
    from settings import secrets
except:
    from settings import secrets_template as secrets

DEFAULT_APP_CONFIG = {
    "webapp2_extras.sessions": {
        "secret_key": secrets.COOKIE_KEY,
        "session_max_age": SECS_PER_WEEK,
        "cookie_args": {"max_age": SECS_PER_WEEK},
        "cookie_name": COOKIE_NAME,
    },
    "webapp2_extras.jinja2": {"template_path": runtime_helpers.get_relative_path()},
}