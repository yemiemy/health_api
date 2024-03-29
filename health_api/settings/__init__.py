from django.core.exceptions import ImproperlyConfigured

import json

with open("/etc/health_api_config.json") as config_file:
    config = json.load(config_file)

ENV_SETTING = "ENVIRONMENT_SETTING"

current_env = config.get(ENV_SETTING)

if current_env == "PROD":
    from health_api.settings.prod import *
elif current_env == "TESTING":
    from health_api.settings.testing import *
elif current_env == "DEV":
    from health_api.settings.dev import *
else:
    raise ImproperlyConfigured(
        "Set {} environment variable.".format(ENV_SETTING)
    )
