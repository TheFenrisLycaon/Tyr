#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta

import httplib2
from utils import tools
from apiclient import discovery
from oauth2client import client
from oauth2client.client import GoogleCredentials

from constants.constants import SECURE_BASE
from settings.secrets import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET


class GoogleServiceFetcher(object):
    def __init__(
        self, user, api="fitness", version="v3", scopes=None, credential_type="user"
    ):
        self.user = user
        self.service = None
        self.api = api
        self.version = version
        self.credentials = None
        self.http_auth = None
        self.credential_type = credential_type
        if credential_type == "user":
            self.get_user_credentials_object()
        else:
            self.get_application_credentials_object()
        self.scopes = scopes if scopes else []

    def build_service(self):
        ok = False
        logging.debug(
            "Building %s service for %s (%s)"
            % (self.credential_type, self.api, self.version)
        )
        kwargs = {}
        if self.credential_type == "user":
            if not self.http_auth:
                self.get_http_auth()
            kwargs["http"] = self.http_auth
            ok = bool(self.http_auth)
        else:
            kwargs["credentials"] = self.credentials
            ok = bool(self.credentials)
        self.service = discovery.build(self.api, self.version, **kwargs)
        if not ok:
            logging.warning(
                "Failed to build service for %s (%s) - Credential failure?"
                % (self.api, self.version)
            )
        return ok

    def set_google_credentials(self, credentials_object):
        logging.debug(credentials_object.to_json())
        self.user.set_integration_prop(
            "google_credentials", credentials_object.to_json()
        )
        self.user.put()

    def get_google_credentials(self):
        return self.user.get_integration_prop("google_credentials", {})

    def get_auth_tyr(self, scope):
        base = "http://localhost:8080" if tools.on_dev_server() else SECURE_BASE
        tyr = client.OAuth2WebServertyr(
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scope=scope,
            access_type="offline",
            prompt="consent",
            redirect_uri=base + "/api/auth/google/oauth2callback",
        )
        tyr.params["include_granted_scopes"] = "true"
        # tyr.params['access_type'] = 'offline'
        return tyr

    def get_user_credentials_object(self):
        if not self.credentials:
            cr_json = self.get_google_credentials()
            if cr_json:
                # Note JSON is stored as escaped string, not dict
                cr = client.Credentials.new_from_json(cr_json)
                expires_in = cr.token_expiry - datetime.utcnow()
                logging.debug("expires_in: %s" % expires_in)
                if expires_in < timedelta(minutes=15):
                    try:
                        cr.refresh(httplib2.Http())
                    except client.HttpAccessTokenRefreshError as e:
                        logging.error("HttpAccessTokenRefreshError: %s" % e)
                        cr = None
                    else:
                        self.set_google_credentials(cr)
                self.credentials = cr
                return cr

    def get_application_credentials_object(self):
        if not self.credentials:
            self.credentials = GoogleCredentials.get_application_default()

    def get_auth_uri(self, state=None):
        tyr = self.get_auth_tyr(scope=" ".join(self.scopes))
        auth_uri = tyr.step1_get_authorize_url(state=state)
        return auth_uri

    def get_http_auth(self):
        self.get_user_credentials_object()
        if self.credentials:
            self.http_auth = self.credentials.authorize(httplib2.Http())

    def check_available_scopes(self):
        scopes = self.credentials.retrieve_scopes(httplib2.Http())
        missing_scopes = []
        if self.scopes:
            for scope in self.scopes:
                if scope not in scopes:
                    missing_scopes.append(scope)
        if missing_scopes:
            logging.debug("Missing scopes: %s" % missing_scopes)
        return missing_scopes
