# Superset specific config
ROW_LIMIT = 5000


import os

from cachelib.file import FileSystemCache

# Flask App Builder configuration
# Your App secret key will be used for securely signing the session cookie
# and encrypting sensitive information on the database
# Make sure you are changing this key for your deployment with a strong key.
# Alternatively you can set it with `SUPERSET_SECRET_KEY` environment variable.
# You MUST set this for production environments or the server will not refuse
# to start and you will see an error in the logs accordingly.
SECRET_KEY = 'thisisjulysecretkeythisisjulysecretkey11'

# The SQLAlchemy connection string to your database backend
# This connection defines the path to the database that stores your
# superset metadata (slices, connections, tables, dashboards, ...).
# Note that the connection information to connect to the datasources
# you want to explore are managed directly in the web UI
SQLALCHEMY_DATABASE_URI = 'sqlite:////app/superset_home/superset1.db'

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = True
# Add endpoints that need to be exempt from CSRF protection
WTF_CSRF_EXEMPT_LIST = []
# A CSRF token that expires in 1 year
WTF_CSRF_TIME_LIMIT = 60 * 60 * 24 * 365

# Set this API key to enable Mapbox visualizations
MAPBOX_API_KEY = ''

#GLOBALS FOR APP Builder

# Uncomment to setup Your App name
APP_NAME = "SmartPulse"

# Specify the App icon
APP_ICON = "/static/assets/images/superset-logo-horiz.png"

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CELERY_DB = os.getenv("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = os.getenv("REDIS_RESULTS_DB", "1")

RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")

CACHE_CONFIG = {
"CACHE_TYPE": "RedisCache",
"CACHE_DEFAULT_TIMEOUT": 300,
"CACHE_KEY_PREFIX": "superset_",
"CACHE_REDIS_HOST": REDIS_HOST,
"CACHE_REDIS_PORT": REDIS_PORT,
"CACHE_REDIS_DB": REDIS_RESULTS_DB,
}
DATA_CACHE_CONFIG = CACHE_CONFIG


#Filterflags
DEFAULT_FEATURE_FLAGS: dict[str, bool] = {
    # Experimental feature introducing a client (browser) cache
    "CLIENT_CACHE": False,  # deprecated
    "DISABLE_DATASET_SOURCE_EDIT": False,  # deprecated
    # When using a recent version of Druid that supports JOINs turn this on
    "DRUID_JOINS": False,
    "DYNAMIC_PLUGINS": False,
    # With Superset 2.0, we are updating the default so that the legacy datasource
    # editor no longer shows. Currently this is set to false so that the editor
    # option does show, but we will be depreciating it.
    "DISABLE_LEGACY_DATASOURCE_EDITOR": True,
    # For some security concerns, you may need to enforce CSRF protection on
    # all query request to explore_json endpoint. In Superset, we use
    # `flask-csrf <https://sjl.bitbucket.io/flask-csrf/>`_ add csrf protection
    # for all POST requests, but this protection doesn't apply to GET method.
    # When ENABLE_EXPLORE_JSON_CSRF_PROTECTION is set to true, your users cannot
    # make GET request to explore_json. explore_json accepts both GET and POST request.
    # See `PR 7935 <https://github.com/apache/superset/pull/7935>`_ for more details.
    "ENABLE_EXPLORE_JSON_CSRF_PROTECTION": False,  # deprecated
    "ENABLE_TEMPLATE_PROCESSING": False,
    "ENABLE_TEMPLATE_REMOVE_FILTERS": True,  # deprecated
    # Allow for javascript controls components
    # this enables programmers to customize certain charts (like the
    # geospatial ones) by inputting javascript in controls. This exposes
    # an XSS security vulnerability
    "ENABLE_JAVASCRIPT_CONTROLS": False,
    "KV_STORE": False,
    # When this feature is enabled, nested types in Presto will be
    # expanded into extra columns and/or arrays. This is experimental,
    # and doesn't work with all nested types.
    "PRESTO_EXPAND_DATA": False,
    # Exposes API endpoint to compute thumbnails
    "THUMBNAILS": False,
    "DASHBOARD_CACHE": False,  # deprecated
    "REMOVE_SLICE_LEVEL_LABEL_COLORS": False,  # deprecated
    "SHARE_QUERIES_VIA_KV_STORE": False,
    "TAGGING_SYSTEM": False,
    "SQLLAB_BACKEND_PERSISTENCE": True,
    "LISTVIEWS_DEFAULT_CARD_VIEW": False,
    # When True, this escapes HTML (rather than rendering it) in Markdown components
    "ESCAPE_MARKDOWN_HTML": False,
    "DASHBOARD_NATIVE_FILTERS": True,  # deprecated
    "DASHBOARD_CROSS_FILTERS": True,
    # Feature is under active development and breaking changes are expected
    "DASHBOARD_NATIVE_FILTERS_SET": False,  # deprecated
    "DASHBOARD_FILTERS_EXPERIMENTAL": False,  # deprecated
    "DASHBOARD_VIRTUALIZATION": False,
    "GLOBAL_ASYNC_QUERIES": False,
    "VERSIONED_EXPORT": True,  # deprecated
    "EMBEDDED_SUPERSET": False,
    # Enables Alerts and reports new implementation
    "ALERT_REPORTS": False,
    "DASHBOARD_RBAC": False,
    "ENABLE_EXPLORE_DRAG_AND_DROP": True,  # deprecated
    "ENABLE_ADVANCED_DATA_TYPES": False,
    # Enabling ALERTS_ATTACH_REPORTS, the system sends email and slack message
    # with screenshot and link
    # Disables ALERTS_ATTACH_REPORTS, the system DOES NOT generate screenshot
    # for report with type 'alert' and sends email and slack message with only link;
    # for report with type 'report' still send with email and slack message with
    # screenshot and link
    "ALERTS_ATTACH_REPORTS": True,
    # Allow users to export full CSV of table viz type.
    # This could cause the server to run out of memory or compute.
    "ALLOW_FULL_CSV_EXPORT": False,
    "GENERIC_CHART_AXES": True,  # deprecated
    "ALLOW_ADHOC_SUBQUERY": False,
    "USE_ANALAGOUS_COLORS": False,
    # Apply RLS rules to SQL Lab queries. This requires parsing and manipulating the
    # query, and might break queries and/or allow users to bypass RLS. Use with care!
    "RLS_IN_SQLLAB": False,
    # Enable caching per impersonation key (e.g username) in a datasource where user
    # impersonation is enabled
    "CACHE_IMPERSONATION": False,
    # Enable caching per user key for Superset cache (not datatabase cache impersonation)
    "CACHE_QUERY_BY_USER": False,
    # Enable sharing charts with embedding
    "EMBEDDABLE_CHARTS": True,
    "DRILL_TO_DETAIL": True,
    "DRILL_BY": False,
    "DATAPANEL_CLOSED_BY_DEFAULT": False,
    "HORIZONTAL_FILTER_BAR": True,
    # The feature is off by default, and currently only supported in Presto and Postgres,
    # and Bigquery.
    # It also needs to be enabled on a per-database basis, by adding the key/value pair
    # `cost_estimate_enabled: true` to the database `extra` attribute.
    "ESTIMATE_QUERY_COST": False,
    # Allow users to enable ssh tunneling when creating a DB.
    # Users must check whether the DB engine supports SSH Tunnels
    # otherwise enabling this flag won't have any effect on the DB.
    "SSH_TUNNELING": False,
    "AVOID_COLORS_COLLISION": True,
    # Set to False to only allow viewing own recent activity
    # or to disallow users from viewing other users profile page
    # Do not show user info or profile in the menu
    "MENU_HIDE_USER_INFO": False,
}


from celery.schedules import crontab

FEATURE_FLAGS = {
    "ALERT_REPORTS": True
}

REDIS_HOST = "superset_cache"
REDIS_PORT = "6379"

class CeleryConfig:
    broker_url = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
    imports = ('superset.sql_lab', "superset.tasks", "superset.tasks.thumbnails", )
    result_backend = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
    worker_prefetch_multiplier = 10
    task_acks_late = True
    task_annotations = {
        'sql_lab.get_sql_results': {
            'rate_limit': '100/s',
        },
        'email_reports.send': {
            'rate_limit': '1/s',
            'time_limit': 600,
            'soft_time_limit': 600,
            'ignore_result': True,
        },
    }
    beat_schedule = {
        'reports.scheduler': {
            'task': 'reports.scheduler',
            'schedule': crontab(minute='*', hour='*'),
        },
        'reports.prune_log': {
            'task': 'reports.prune_log',
            'schedule': crontab(minute=0, hour=0),
        },
    }
CELERY_CONFIG = CeleryConfig

SCREENSHOT_LOCATE_WAIT = 100
SCREENSHOT_LOAD_WAIT = 600

# Slack configuration
SLACK_API_TOKEN = "xoxb-"

# Email configuration
SMTP_HOST =  mail.cms.co.in # CMS HOST
SMTP_PORT = 993 # CMS port
SMTP_STARTTLS = True
SMTP_SSL_SERVER_AUTH = True # If your using an SMTP server with a valid certificate
SMTP_SSL = False
SMTP_USER = "arbaz_shaikh@cms.co.in" # My Username
SMTP_PASSWORD = "Mumbai@123" # email password
SMTP_MAIL_FROM = "arbaz_shaikh@cms.co.in"
EMAIL_REPORTS_SUBJECT_PREFIX = "Smart Pulse" 

# WebDriver configuration
# If you use Firefox, you can stick with default values
# If you use Chrome, then add the following WEBDRIVER_TYPE and WEBDRIVER_OPTION_ARGS
WEBDRIVER_TYPE = "chrome"
WEBDRIVER_OPTION_ARGS = [
    "--force-device-scale-factor=2.0",
    "--high-dpi-support=2.0",
    "--headless",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-extensions",
]

# This is for internal use, you can keep http
WEBDRIVER_BASEURL = "http://superset:8088"
# This is the link sent to the recipient. Change to your domain, e.g. https://superset.mydomain.com
WEBDRIVER_BASEURL_USER_FRIENDLY = "http://localhost:8088"