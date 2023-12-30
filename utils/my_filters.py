import json

import jinja2


def printjson(d):
    if d:
        return jinja2.Markup(json.dumps(d))
    else:
        return "null"
