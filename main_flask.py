from flask import Flask
from google.appengine.api import wrap_wsgi_app

from actions import adminActions
from constants import const
from controllers import api, tasks
from views import views

app = Flask(__name__, config=const.DEFAULT_APP_CONFIG)

app.wsgi_app = wrap_wsgi_app(app.wsgi_app)


# Admin Actions
app.add_url_rule(
    "/admin/gauth/initialize", view_func=adminActions.Init, endpoint="aInit"
)
app.add_url_rule("/admin/gauth/hacks", view_func=adminActions.Hacks)

# API
app.add_url_rule("/api/user/me", view_func=api.UserAPI.update_self, methods=["POST"])
app.add_url_rule("/api/user", view_func=api.UserAPI.list, methods=["GET"])
app.add_url_rule(
    "/api/project/active", view_func=api.ProjectAPI.active, methods=["GET"]
)
app.add_url_rule("/api/project", view_func=api.ProjectAPI.list, methods=["GET"])
app.add_url_rule("/api/project", view_func=api.ProjectAPI.update, methods=["POST"])
app.add_url_rule(
    "/api/project/delete", view_func=api.ProjectAPI.delete, methods=["POST"]
)
app.add_url_rule("/api/habit", view_func=api.HabitAPI.list, methods=["GET"])
app.add_url_rule("/api/habit/recent", view_func=api.HabitAPI.recent, methods=["GET"])
app.add_url_rule("/api/habit/range", view_func=api.HabitAPI.range, methods=["GET"])
app.add_url_rule("/api/habit/toggle", view_func=api.HabitAPI.toggle, methods=["POST"])
app.add_url_rule(
    "/api/habit/increment", view_func=api.HabitAPI.increment, methods=["POST"]
)
app.add_url_rule("/api/habit/commit", view_func=api.HabitAPI.commit, methods=["POST"])
app.add_url_rule("/api/habit/delete", view_func=api.HabitAPI.delete, methods=["POST"])
app.add_url_rule("/api/habit", view_func=api.HabitAPI.update, methods=["POST"])
app.add_url_rule("/api/habit/delete", view_func=api.HabitAPI.delete, methods=["POST"])
app.add_url_rule("/api/habit/<id>", view_func=api.HabitAPI.detail, methods=["GET"])
app.add_url_rule("/api/goal", view_func=api.GoalAPI.list, methods=["GET"])
app.add_url_rule("/api/goal/current", view_func=api.GoalAPI.current, methods=["GET"])
app.add_url_rule("/api/goal", view_func=api.GoalAPI.update, methods=["POST"])
app.add_url_rule("/api/event", view_func=api.EventAPI.list, methods=["GET"])
app.add_url_rule("/api/event", view_func=api.EventAPI.update, methods=["POST"])
app.add_url_rule(
    "/api/event/batch", view_func=api.EventAPI.batch_create, methods=["POST"]
)
app.add_url_rule("/api/event/delete", view_func=api.EventAPI.delete, methods=["POST"])
app.add_url_rule("/api/journal/today", view_func=api.JournalAPI.today, methods=["GET"])
app.add_url_rule("/api/journal/year", view_func=api.JournalAPI.year, methods=["GET"])
app.add_url_rule(
    "/api/journal/submit", view_func=api.JournalAPI.submit, methods=["POST"]
)
app.add_url_rule("/api/journal", view_func=api.JournalAPI.list, methods=["GET"])
app.add_url_rule("/api/journal", view_func=api.JournalAPI.update, methods=["POST"])
app.add_url_rule("/api/snapshot", view_func=api.SnapshotAPI.submit, methods=["POST"])
app.add_url_rule("/api/snapshot", view_func=api.SnapshotAPI.list, methods=["GET"])
app.add_url_rule("/api/tracking", view_func=api.TrackingAPI.list, methods=["GET"])
app.add_url_rule("/api/tracking", view_func=api.TrackingAPI.update, methods=["POST"])
app.add_url_rule("/api/task", view_func=api.TaskAPI.list, methods=["GET"])
app.add_url_rule("/api/task", view_func=api.TaskAPI.update, methods=["POST"])
app.add_url_rule("/api/task/delete", view_func=api.TaskAPI.delete, methods=["POST"])
app.add_url_rule("/api/task/action", view_func=api.TaskAPI.action, methods=["POST"])
app.add_url_rule("/api/readable", view_func=api.ReadableAPI.list, methods=["GET"])
app.add_url_rule("/api/readable", view_func=api.ReadableAPI.update, methods=["POST"])
app.add_url_rule(
    "/api/readable/delete", view_func=api.ReadableAPI.delete, methods=["POST"]
)
app.add_url_rule(
    "/api/readable/batch", view_func=api.ReadableAPI.batch_create, methods=["POST"]
)
app.add_url_rule(
    "/api/readable/random", view_func=api.ReadableAPI.random_batch, methods=["GET"]
)
app.add_url_rule(
    "/api/readable/search", view_func=api.ReadableAPI.search, methods=["GET"]
)
app.add_url_rule("/api/quote", view_func=api.QuoteAPI.list, methods=["GET"])
app.add_url_rule("/api/quote", view_func=api.QuoteAPI.update, methods=["POST"])
app.add_url_rule(
    "/api/quote/batch", view_func=api.QuoteAPI.batch_create, methods=["POST"]
)
app.add_url_rule(
    "/api/quote/random", view_func=api.QuoteAPI.random_batch, methods=["GET"]
)
app.add_url_rule("/api/quote/search", view_func=api.QuoteAPI.search, methods=["GET"])
app.add_url_rule("/api/quote/action", view_func=api.QuoteAPI.action, methods=["POST"])
app.add_url_rule("/api/quote/delete", view_func=api.QuoteAPI.delete, methods=["POST"])
app.add_url_rule("/api/analysis", view_func=api.AnalysisAPI.get, methods=["GET"])
app.add_url_rule("/api/journaltag", view_func=api.JournalTagAPI.list, methods=["GET"])
app.add_url_rule("/api/report", view_func=api.ReportAPI.list, methods=["GET"])
app.add_url_rule(
    "/api/report/generate", view_func=api.ReportAPI.generate, methods=["POST"]
)
app.add_url_rule("/api/report/serve", view_func=api.ReportAPI.serve, methods=["GET"])
app.add_url_rule("/api/report/delete", view_func=api.ReportAPI.delete, methods=["POST"])
app.add_url_rule("/api/feedback", view_func=api.FeedbackAPI.submit, methods=["POST"])
app.add_url_rule("/api/auth/google_login", view_func=api.AuthenticationAPI.google_login)
app.add_url_rule("/api/auth/google_auth", view_func=api.AuthenticationAPI.google_auth)
app.add_url_rule(
    "/api/auth/google/token",
    view_func=api.AuthenticationAPI.google_token,
    methods=["POST"],
)
app.add_url_rule(
    "/api/auth/google/oauth2callback",
    view_func=api.AuthenticationAPI.google_oauth2_callback,
)
app.add_url_rule(
    "/api/auth/google/<service_name>/authenticate",
    view_func=api.AuthenticationAPI.google_service_authenticate,
)
app.add_url_rule("/api/auth/fbook_auth", view_func=api.AuthenticationAPI.fbook_auth)
app.add_url_rule("/api/auth/logout", view_func=api.AuthenticationAPI.logout)

# Integrations
app.add_url_rule(
    "/api/integrations/update_integration_settings",
    view_func=api.IntegrationsAPI.update_integration_settings,
    methods=["POST"],
)
app.add_url_rule(
    "/api/integrations/goodreads",
    view_func=api.IntegrationsAPI.goodreads_shelf,
    methods=["GET"],
)
# Integrations (continued)
app.add_url_rule(
    "/api/integrations/pocket",
    view_func=api.IntegrationsAPI.pocket_sync,
    methods=["GET"],
)
app.add_url_rule(
    "/api/integrations/pocket/authenticate",
    view_func=api.IntegrationsAPI.pocket_authenticate,
    methods=["POST"],
)
app.add_url_rule(
    "/api/integrations/pocket/authorize",
    view_func=api.IntegrationsAPI.pocket_authorize,
    methods=["POST"],
)
app.add_url_rule(
    "/api/integrations/pocket/disconnect",
    view_func=api.IntegrationsAPI.pocket_disconnect,
    methods=["POST"],
)
app.add_url_rule(
    "/api/integrations/evernote/authenticate",
    view_func=api.IntegrationsAPI.evernote_authenticate,
    methods=["POST"],
)
app.add_url_rule(
    "/api/integrations/evernote/authorize",
    view_func=api.IntegrationsAPI.evernote_authorize,
    methods=["POST"],
)
app.add_url_rule(
    "/api/integrations/evernote/disconnect",
    view_func=api.IntegrationsAPI.evernote_disconnect,
    methods=["POST"],
)
app.add_url_rule(
    "/api/integrations/evernote/webhook",
    view_func=api.IntegrationsAPI.evernote_webhook,
    methods=["GET"],
)

# Agent
app.add_url_rule(
    "/api/agent/apiai/request", view_func=api.AgentAPI.apiai_request, methods=["POST"]
)
app.add_url_rule("/api/agent/fbook/request", view_func=api.AgentAPI.fbook_request)
app.add_url_rule("/api/agent/tyrapp/request", view_func=api.AgentAPI.tyrapp_request)
app.add_url_rule("/api/agent/spoof", view_func=api.AgentAPI.spoof, methods=["POST"])

# Reports
app.add_url_rule("/api/report/serve", view_func=api.ReportAPI.serve, methods=["GET"])

# Cron jobs (see cron.yaml)
app.add_url_rule("/cron/readables/sync", view_func=tasks.SyncReadables)
app.add_url_rule("/cron/pull/github", view_func=tasks.SyncGithub)
app.add_url_rule("/cron/pull/google_fit", view_func=tasks.SyncFromGoogleFit)
app.add_url_rule("/cron/push/bigquery", view_func=tasks.PushToBigQuery)
app.add_url_rule("/cron/reports/delete_old", view_func=tasks.DeleteOldReports)
app.add_url_rule("/_ah/warmup", view_func=tasks.WarmupHandler)

# Private app (react)
app.add_url_rule(r"/<:.*>", view_func=views.App, endpoint="PrivateApp")

if __name__ == "__main__":
    app.run(debug=True)
