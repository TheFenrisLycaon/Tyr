#!/usr/bin/python
# -*- coding: utf8 -*-

import imp
import json
from datetime import datetime

from controllers.main import app as tst_app
from models.models import Goal, Habit, Task

from .base_test_case import BaseTestCase

try:
    imp.find_module("secrets", ["settings"])
except ImportError:
    from settings import secrets_template as secrets
else:
    from settings import secrets


class DummyRequest:
    def __init__(self, body):
        self.body = json.dumps(body)


FB_ID = "1182039228580000"


class APIAITestCase(BaseTestCase):
    def setUp(self):
        self.set_application(tst_app)
        self.setup_testbed()
        self.init_datastore_stub()
        self.init_memcache_stub()
        self.init_taskqueue_stub()
        self.init_mail_stub()
        self.register_search_api_stub()
        self.init_app_basics()

        self.u = u = self.users[0]
        self.u.Update(name="George", fb_id=FB_ID)
        self.u.put()
        h = Habit.Create(u)
        h.Update(name="Run")
        h.put()
        t = Task.Create(u, "Dont forget the milk")
        t.put()
        g = Goal.CreateMonthly(u, date=datetime.today().date())
        g.Update(text=["Get it done", "Also get exercise"])
        g.put()

    def test_a_request(self):
        access_token = self.u.aes_access_token(client_id="google")
        data = {
            "lang": "en",
            "status": {"code": 200, "errorType": "success"},
            "timestamp": "2017-03-18T11:06:39.683Z",
            "sessionId": "1489835199537",
            "result": {
                "source": "agent",
                "score": 1.0,
                "speech": "",
                "fulfillment": {"speech": "", "messages": [{"type": 0, "speech": ""}]},
                "parameters": {},
                "contexts": [
                    {
                        "name": "google_assistant_welcome",
                        "parameters": {},
                        "lifespan": 0,
                    }
                ],
                "resolvedQuery": "what are my tasks",
                "metadata": {
                    "intentId": "X",
                    "webhookForSlotFillingUsed": "false",
                    "intentName": "Task Request",
                    "webhookUsed": "true",
                },
                "action": "input.task_view",
                "actionIncomplete": False,
            },
            "id": "32fc0ce2-16a3-4d33-bf19-XXXXXXXXX",
            "originalRequest": {
                "source": "google",
                "data": {
                    "device": {},
                    "inputs": [
                        {
                            "rawInputs": [
                                {
                                    "query": "at Tyr what are my tasks",
                                    "annotationSets": [
                                        {
                                            "domain": 1,
                                            "annotations": [
                                                {
                                                    "confidence": 1099999.998,
                                                    "startPosition": 3,
                                                    "length": 4,
                                                }
                                            ],
                                        }
                                    ],
                                    "inputType": 2,
                                }
                            ],
                            "intent": "actions.intent.MAIN",
                            "arguments": [
                                {
                                    "text_value": "what are my tasks",
                                    "raw_text": "what are my tasks",
                                    "name": "trigger_query",
                                }
                            ],
                        }
                    ],
                    "user": {"accessToken": access_token, "userId": "XXX"},
                    "surface": {
                        "capabilities": [{"name": "actions.capability.AUDIO_OUTPUT"}]
                    },
                    "conversation": {"conversationId": "1489835199537", "type": 1},
                },
            },
        }
        # Reuqests for tasks
        res = self.post(
            "/api/agent/apiai/request",
            json.dumps(data),
            headers={"Auth-Key": secrets.API_AI_AUTH_KEY},
        )
        self.assertOK(res)
        res_body = json.loads(res.normal_body)
        self.assertEqual(
            res_body.get("speech"),
            "You haven't completed any tasks yet. You still need to do 'Dont forget the milk'.",
        )
