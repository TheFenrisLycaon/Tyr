#!/usr/bin/python
# -*- coding: utf-8 -*-

# API calls to interact with API.AI (Google Assistant / Actions / Home, Facebook Messenger)

import imp
import json
import logging
import pickle
import random
import re
from datetime import datetime, time, timedelta

from utils import tools
from google.appengine.api import memcache, urlfetch
from google.appengine.ext import ndb

from constants.constants import (GOAL, HABIT, HABIT_COMMIT_REPLIES,
                                 HABIT_DONE_REPLIES, JOURNAL, SECURE_BASE,
                                 TASK)
from models.models import Goal, Habit, HabitDay, MiniJournal, Task, User

try:
    imp.find_module("secrets", ["settings"])
except ImportError:
    from settings import secrets_template as secrets
else:
    from settings import secrets

AGENT_GOOGLE_ASST = 1
AGENT_FBOOK_MESSENGER = 2
AGENT_tyr_APP = 3

CONVO_EXPIRE_MINS = 5

HELP_TEXT = "With the tyr agent, you can track top tasks each day, habits to build, and monthly and annual goals. You can also submit daily journals at the end of each day to track anything you want. I'm still in beta."


class ConversationState(object):
    def __init__(self, cache_key, type="journal"):
        self.dt_start = datetime.now()
        self.dt_expire = None
        self.last_message_to_user = None
        self.next_expected_pattern = None
        self.next_store_key = None
        self.store_array = False
        self.store_number = False
        self.cache_key = cache_key
        self.state = {}  # Hold state
        self.response_data = {}
        self.type = type
        self.update_expiration()

    def update_expiration(self):
        self.dt_expire = datetime.now() + timedelta(seconds=60 * CONVO_EXPIRE_MINS)

    def expired(self):
        return datetime.now() > self.dt_expire

    def add_message_from_user(self, from_user):
        success = True
        if self.next_expected_pattern:
            m = re.match(self.next_expected_pattern, from_user)
            if m and self.next_store_key:
                logging.debug(
                    "Setting response data %s->%s" % (self.next_store_key, from_user)
                )
                value = from_user
                if self.store_number:
                    value = tools.safe_number(value)
                if self.store_array:
                    if self.next_store_key not in self.response_data:
                        self.response_data[self.next_store_key] = []
                    self.response_data[self.next_store_key].append(value)
                else:
                    self.response_data[self.next_store_key] = value
            else:
                success = False
        self.update_expiration()
        return success

    def invalid_reply(self):
        suffix = ""
        if self.store_number:
            suffix = " " + JOURNAL.INVALID_SUFFIX_NUMERIC
        return JOURNAL.INVALID_REPLY + suffix

    def set_message_to_user(self, to_user):
        self.last_message_to_user = to_user

    def set_state(self, prop, value):
        logging.debug("Setting conversation state %s->%s" % (prop, value))
        self.state[prop] = value

    def expect_reply(
        self, pattern, store_key=None, store_array=False, store_number=False
    ):
        self.next_expected_pattern = pattern
        if store_key:
            self.next_store_key = store_key
        self.store_array = store_array
        self.store_number = store_number


class ConversationAgent(object):
    COMPLY_BANTER = ["Sure", "No problem", "Of course", "Absolutely", "OK"]

    HELLO_BANTER = ["Hi there!", "Hi!", "Hello!", "Hi", "Hello"]

    HELLO_QUESTION_BANTER = [
        "I'm great",
        "Just fine",
        "Swell!",
        "Wonderful!",
        "Taking it easy",
        "Perfect!",
        "I'm great!",
    ]

    def __init__(self, type=AGENT_GOOGLE_ASST, user=None):
        self.type = type
        self.user = user
        self.cs = None

    def _convo_mckey(self):
        if self.user:
            return "conversation_uid:%s" % self.user.key.id()

    def _get_conversation_state(self):
        if self._convo_mckey():
            _cs = memcache.get(self._convo_mckey())
            cs = None
            if _cs:
                cs = pickle.loads(_cs)
                if cs.expired():
                    self._expire_conversation()
                    cs = None
            return cs

    def _create_conversation_state(self):
        # New conversation state
        return ConversationState(self._convo_mckey())

    def _expire_conversation(self):
        memcache.delete(self._convo_mckey())

    def _set_conversation_state(self):
        if self.cs:
            pickled = pickle.dumps(self.cs)
            memcache.set(self._convo_mckey(), pickled, 60 * CONVO_EXPIRE_MINS)

    def _quick_replies(self, buttons):
        """
        buttons are list of (title, payload) tuples
        """
        return {
            "quick_replies": [
                {"content_type": "text", "title": b[0], "payload": b[1]}
                for b in buttons
            ]
        }

    def _comply_banter(self):
        return random.choice(ConversationAgent.COMPLY_BANTER)

    def _user_disconnect(self, session=None):
        if self.type == AGENT_FBOOK_MESSENGER:
            self.user.fb_id = None
            self.user.put()
        elif self.type == AGENT_GOOGLE_ASST:
            self.user.g_id = None
            self.user.put()
            if "user" in session:
                for key in list(session.keys()):
                    del session[key]

        return "Alright, you're disconnected."

    def _hello(self, question=False):
        if question:
            return random.choice(ConversationAgent.HELLO_BANTER)
        else:
            return random.choice(ConversationAgent.HELLO_BANTER)

    def _journal(self, message=""):
        DONE_MESSAGES = ["done", "that's all", "exit", "finished", "no"]
        MODES = ["questions", "tasks", "end"]
        settings = tools.getJson(self.user.settings, {})
        questions = settings.get("journals", {}).get("questions", [])
        end_convo = False
        if questions:
            jrnl = MiniJournal.Get(self.user)
            if jrnl:
                return (JOURNAL.ALREADY_SUBMITTED_REPLY, True)
            else:
                if not self.cs:
                    self.cs = self._create_conversation_state()
                    self.cs.set_state("mode", "questions")
                mode = self.cs.state.get("mode")
                mode_finished = False
                save_response = True
                last_question = None
                # Receive user message
                if mode == "tasks":
                    is_done = message.lower().strip() in DONE_MESSAGES
                    mode_finished = is_done
                    save_response = not is_done
                elif mode == "questions":
                    last_q_index = self.cs.state.get("last_q_index", -1)
                    last_question = last_q_index == len(questions) - 1
                    mode_finished = last_question
                    save_response = True
                if save_response:
                    successful_add = self.cs.add_message_from_user(message)
                    if not successful_add:
                        reply = (
                            self.cs.invalid_reply()
                            if mode == "questions"
                            else JOURNAL.INVALID_TASK
                        )
                        return (reply, False)
                mode_index = MODES.index(mode)
                if mode_finished:
                    mode = MODES[mode_index + 1]
                    self.cs.set_state("mode", mode)
                reply = None
                # Generate next reply
                if mode == "questions":
                    next_q_index = last_q_index + 1
                    q = questions[next_q_index]
                    reply = q.get("text")
                    name = q.get("name")
                    response_type = q.get("response_type")
                    pattern = JOURNAL.PATTERNS.get(response_type)
                    store_number = response_type in JOURNAL.NUMERIC_RESPONSES
                    self.cs.expect_reply(
                        pattern, name, store_number=store_number
                    )  # Store as name
                    self.cs.set_state("last_q_index", next_q_index)
                elif mode == "tasks":
                    # Ask to add tasks
                    tasks = self.cs.response_data.get("tasks", [])
                    additional = len(tasks) > 0
                    reply = (
                        JOURNAL.TOP_TASK_PROMPT_ADDTL
                        if additional
                        else JOURNAL.TOP_TASK_PROMPT
                    )
                    self.cs.expect_reply(
                        JOURNAL.PTN_TEXT_RESPONSE, "tasks", store_array=True
                    )  # Store as name
                elif mode == "end":
                    # Finish and submit
                    task_names = []
                    if "tasks" in self.cs.response_data:
                        task_names = self.cs.response_data.pop("tasks")
                    jrnl = MiniJournal.Create(self.user)
                    jrnl.Update(data=self.cs.response_data)
                    jrnl.parse_tags()
                    jrnl.put()
                    tasks = []
                    if task_names:
                        for tn in task_names:
                            task = Task.Create(self.user, tn)
                            tasks.append(task)
                    ndb.put_multi(tasks)
                    reply = "Report submitted!"
                    end_convo = True
                if reply:
                    self.cs.set_message_to_user(reply)
                if end_convo:
                    self._expire_conversation()
                else:
                    self._set_conversation_state()
                return (reply, end_convo)
        else:
            return ("TODO", True)

    def _goals_set(self):
        return GOAL.SET_INFO

    def _goals_request(self):
        [annual, monthly, longterm] = Goal.Current(self.user)
        speech = None
        g = None
        if monthly:
            g = monthly
            speech = "Goals for %s. " % datetime.strftime(g.date, "%B %Y")
        elif annual:
            g = annual
            speech = "Goals for %s. " % g.year()
        if g:
            if g.text:
                for i, text in enumerate(g.text):
                    speech += "%d: %s. " % (i + 1, text)
            else:
                speech = "No goals yet"
        else:
            speech = "You haven't set up any goals yet. " + GOAL.SET_INFO
        return speech

    def _tasks_request(self):
        tasks = Task.Recent(self.user)
        tasks_undone = []
        n_done = Task.CountCompletedSince(
            self.user, datetime.combine(datetime.today(), time(0, 0))
        )
        for task in tasks:
            if not task.is_done():
                tasks_undone.append(task.title)
        if n_done:
            text = "You've completed %d %s for today." % (
                n_done,
                tools.pluralize("task", n_done),
            )
        else:
            text = "You haven't completed any tasks yet."
        if tasks_undone:
            text += " You still need to do %s." % tools.english_list(tasks_undone)
        if not n_done and not tasks_undone:
            text += " Try adding tasks by saying 'add task Q2 planning'"
        return text

    def _add_task(self, task_name):
        if task_name:
            task = Task.Create(self.user, task_name)
            task.put()
            return self._comply_banter() + ". Task added."
        else:
            return (
                "Sorry, I couldn't add your task. Try saying: 'Add task finish report'"
            )

    def _habit_add(self, habit):
        h = Habit.Create(self.user)
        h.Update(name=habit)
        h.put()
        return self._comply_banter() + ". Habit '%s' added." % h.name

    def _habit_or_task_report(self, item_name):
        """
        Mark a habit or a task as complete
        """
        handled = False
        speech = None
        if item_name:
            habits = Habit.Active(self.user)
            for h in habits:
                if item_name.lower() in h.name.lower():
                    d = self.user.local_time().date()
                    encourage = random.choice(HABIT_DONE_REPLIES)
                    if h.has_daily_count():
                        done, hd = HabitDay.Increment(h, d)
                        speech = "%s The count of '%s' has been increased to %d " % (
                            encourage,
                            h.name,
                            hd.count,
                        )
                        remaining = h.tgt_daily - hd.count
                        speech += (
                            "(habit complete!)"
                            if not remaining
                            else "(%d to go)" % remaining
                        )
                    else:
                        done, hd = HabitDay.Toggle(h, d, force_done=True)
                        speech = "%s '%s' is marked as complete." % (encourage, h.name)
                    handled = True
                    break
            if not handled:
                # Check tasks
                tasks = Task.Recent(self.user)
                for t in tasks:
                    if item_name.lower() in t.title.lower():
                        t.mark_done()
                        t.put()
                        speech = "Task '%s' is marked as complete." % (t.title)
                        handled = True
                        break

            if not handled:
                speech = "I'm not sure what you mean by '%s'." % item_name
        else:
            speech = "I couldn't tell what habit or task you completed."
        return speech

    def _habit_commit(self, habit_param_raw):
        handled = False
        speech = None
        if habit_param_raw:
            habits = Habit.Active(self.user)
            for h in habits:
                # TODO: Flexible fuzzy match?
                if (
                    habit_param_raw.lower() in h.name.lower()
                    or h.name.lower() in habit_param_raw.lower()
                ):
                    # TODO: Timezone?
                    hd = HabitDay.Commit(h, datetime.today().date())
                    encourage = random.choice(HABIT_COMMIT_REPLIES)
                    speech = "You've committed to '%s' today. %s" % (h.name, encourage)
                    handled = True
                    break
            if not handled:
                speech = (
                    "I'm not sure what you mean by '%s'. You may need to create a habit before you can commit to it."
                    % habit_param_raw
                )
        else:
            speech = "I couldn't tell what habit you want to commit to."
        return speech

    def _habit_status(self):
        habits = Habit.All(self.user)
        today = self.user.local_time().date()
        habitday_keys = [
            ndb.Key("HabitDay", HabitDay.ID(h, today), parent=self.user.key)
            for h in habits
        ]
        habitdays = ndb.get_multi(habitday_keys)
        n_habits_done = 0
        habits_committed_undone = []
        habits_done = []
        for hd in habitdays:
            if hd:
                habit = hd.habit.get()
                if hd.committed and not hd.done:
                    if habit:
                        habits_committed_undone.append(habit.name)
                if hd.done:
                    habits_done.append(habit.name)
                    n_habits_done += 1
        if habits:
            if n_habits_done:
                text = "Good work on doing %d %s (%s)!" % (
                    n_habits_done,
                    tools.pluralize("habit", n_habits_done),
                    tools.english_list(habits_done),
                )
            else:
                text = "No habits done yet."
            if habits_committed_undone:
                text += " Don't forget you've committed to %s." % tools.english_list(
                    habits_committed_undone
                )
        else:
            text = "You haven't added any habits yet. Try saying 'add habit run'"
        return text

    def _status_request(self):
        habit_text = self._habit_status()
        address = "Alright %s." % self.user.first_name() if self.user.name else ""
        task_text = self._tasks_request()
        speech = " ".join([address, task_text, habit_text])
        return speech

    def respond_to_action(self, action, parameters=None, session=None):
        speech = None
        end_convo = True
        if not parameters:
            parameters = {}
        data = {}
        if self.user:
            if action == "input.disconnect":
                speech = self._user_disconnect(session=session)
            elif action == "input.hello":
                speech = self._hello()
            elif action == "input.hello_question":
                speech = self._hello(question=True)
            elif action == "input.status_request":
                speech = self._status_request()
            elif action == "input.goals_request":
                speech = self._goals_request()
            elif action == "input.goals_set":
                speech = self._goals_set()
            elif action == "input.habit_or_task_report":
                speech = self._habit_or_task_report(parameters.get("habit_or_task"))
            elif action == "input.habit_commit":
                speech = self._habit_commit(parameters.get("habit"))
            elif action == "input.task_add":
                speech = self._add_task(parameters.get("task_name"))
            elif action == "input.task_view":
                speech = self._tasks_request()
            elif action == "input.habit_add":
                speech = self._habit_add(parameters.get("habit"))
            elif action == "input.habit_status":
                speech = self._habit_status()
            elif action == "input.journal":
                speech, end_convo = self._journal(parameters.get("message"))
            elif action == "input.help_habits":
                speech = ". ".join([self._comply_banter(), HABIT.HELP])
                data = self._quick_replies(
                    [("Learn about Journals", "input.help_journals")]
                )
            elif action == "input.help_journals":
                speech = ". ".join([self._comply_banter(), JOURNAL.HELP])
                data = self._quick_replies([("Learn about Tasks", "input.help_tasks")])
            elif action == "input.help_tasks":
                speech = ". ".join([self._comply_banter(), TASK.HELP])
                data = self._quick_replies([("Learn about Goals", "input.help_goals")])
            elif action == "input.help_goals":
                speech = ". ".join([self._comply_banter(), GOAL.HELP])
                data = self._quick_replies(
                    [("Learn about Habits", "input.help_habits")]
                )
            elif action == "GET_STARTED":
                speech = "Welcome to tyr! " + HELP_TEXT
                data = self._quick_replies(
                    [("Learn about Habits", "input.help_habits")]
                )
            elif action == "input.help":
                speech = HELP_TEXT
                data = self._quick_replies(
                    [("Learn about Habits", "input.help_habits")]
                )
                end_convo = False
        else:
            speech = "To get started with tyr, please link your account with tyr"
            if self.type == AGENT_FBOOK_MESSENGER:
                data = {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "button",
                            "text": speech,
                            "buttons": [
                                {
                                    "type": "account_link",
                                    "url": SECURE_BASE + "/auth/fbook",
                                }
                            ],
                        },
                    }
                }
        return (speech, data, end_convo)

    def _process_pattern(self, pattern):
        return tools.variable_replacement(
            pattern,
            {
                "HABIT_PATTERN": "'?\"?(?P<habit>[a-zA-Z ]+)'?\"?",
                "HABIT_OR_TASK_PATTERN": "'?\"?(?P<habit_or_task>[a-zA-Z ']+)'?\"?",
                "TASK_PATTERN": "'?\"?(?P<task_name>[a-zA-Z ']{5,50})'?\"?",
            },
        )

    def parse_message(self, message):
        action = None
        parameters = None
        self.cs = self._get_conversation_state()
        in_convo = self.cs is not None
        if in_convo:
            if self.cs.type == "journal":
                # Journal report conversation ongoing
                action = "input.journal"
                parameters = {"message": message}
        else:
            LOOKUP = [
                (
                    r"(?:what are my|remind me my|tell me my|monthly|current|my|view) goals",
                    "input.goals_request",
                ),
                (r"(?:set ?up|create|add|set my|set) goals", "input.goals_set"),
                (
                    r"(?:how am i doing|my status|tell me about my day)",
                    "input.status_request",
                ),
                (
                    r"(?:how do|tell me about|more info|learn about|help on|help with|what are) (?:tasks)",
                    "input.help_tasks",
                ),
                (
                    r"(?:how do|tell me about|more info|learn about|help on|help with|what are) (?:habits)",
                    "input.help_habits",
                ),
                (
                    r"(?:how do|tell me about|more info|learn about|help on|help with|what are) (?:journals|journaling|daily journals)",
                    "input.help_journals",
                ),
                (
                    r"(?:how do|tell me about|more info|learn about|help on|help with) (?:goals|monthly goals|goal tracking)",
                    "input.help_goals",
                ),
                (
                    r"(?:mark|set) [HABIT_OR_TASK_PATTERN] as (?:done|complete|finished)",
                    "input.habit_or_task_report",
                ),
                (
                    r"(?:mark|set) [HABIT_OR_TASK_PATTERN] (?:done|complete|finished)",
                    "input.habit_or_task_report",
                ),
                (
                    r"(?:habit|task)(?: done| complete| finished):? [HABIT_OR_TASK_PATTERN]",
                    "input.habit_or_task_report",
                ),
                (
                    r"(?:i finished|just finished|completed|task done|habit done) [HABIT_OR_TASK_PATTERN]",
                    "input.habit_or_task_report",
                ),
                (
                    r"(?:add habit|new habit|create habit)[:-]? [HABIT_PATTERN]",
                    "input.habit_add",
                ),
                (
                    r"(?:commit to|promise to|i will|planning to|going to) [HABIT_PATTERN] (?:today|tonight|this evening|later)",
                    "input.habit_commit",
                ),
                (
                    r"(?:my habits|view habits|habit progress|habits today)",
                    "input.habit_status",
                ),
                (
                    r"(?:add task|set task|new task|remind me to) [TASK_PATTERN]",
                    "input.task_add",
                ),
                (
                    r"(?:my tasks|my to ?do list|view tasks|tasks today|today\'?s tasks)",
                    "input.task_view",
                ),
                (r"(?:daily report|daily journal)", "input.journal"),
                (
                    r"(?:what up|what\'s up|how are you|how\'s it going|what\'s new|you\'re well\?)",
                    "input.hello_question",
                ),
                (
                    r"(?:help me|show commands|how does this work|what can i do|what can I say)",
                    "input.help",
                ),
                (r"(?:^hi$|^hello$|^yo$|i see you|^hey tyr$)", "input.hello"),
                (r"^(help|\?\?\?$)", "input.help"),
                (r"^disconnect$", "input.disconnect"),
            ]
            for lookup in LOOKUP:
                pattern, pattern_action = lookup
                m = re.search(
                    self._process_pattern(pattern), message, flags=re.IGNORECASE
                )
                if m:
                    action = pattern_action
                    if m.groupdict():
                        parameters = m.groupdict()
                    break
        return (action, parameters)


class FacebookAgent(ConversationAgent):
    REQ_UNKNOWN = 1
    REQ_MESSAGE = 2
    REQ_POSTBACK = 3
    REQ_ACCOUNT_LINK = 4

    def __init__(self, request, type=AGENT_FBOOK_MESSENGER, user=None):
        super(FacebookAgent, self).__init__(type=type, user=user)
        self.message_data = {}
        self.reply = None
        self.md = {}  # To populate with entry.messaging[0]
        self.request_type = None
        self.body = tools.getJson(request.body)
        if not user:
            self._get_fbook_user()
        self._get_request_type()
        logging.debug(
            "Authenticated user: %s. Type: %s" % (self.user, self.request_type)
        )
        logging.debug(self.body)
        self._process_request()

    def _link_account(self, psid, account_linking):
        status = account_linking.get("status")
        if status == "linked":
            authcode = account_linking.get("authorization_code")
            user_id = authcode
            logging.debug("Linking user: %s" % authcode)
            self.request_type = FacebookAgent.REQ_ACCOUNT_LINK
            self.user = User.get_by_id(int(user_id))
            if self.user and psid:
                self.user.fb_id = psid
                self.user.put()

    def _get_fbook_user(self):
        entry = self.body.get("entry", [])
        if entry:
            messaging = entry[0].get("messaging")
            if messaging:
                self.md = md = messaging[0]
                account_linking = md.get("account_linking", {})
                sender = md.get("sender", {})
                self.fb_id = psid = sender.get("id")
                if account_linking:
                    # Handle account linking
                    self._link_account(psid, account_linking)
                if not self.user and psid:
                    self.user = User.query().filter(User.fb_id == psid).get()
        else:
            logging.debug("malformed")

    def _get_request_type(self):
        if not self.request_type:
            if "message" in self.md:
                self.request_type = FacebookAgent.REQ_MESSAGE
            elif "postback" in self.md:
                self.request_type = FacebookAgent.REQ_POSTBACK
            else:
                self.request_type = FacebookAgent.REQ_UNKNOWN

    def _get_fbook_message(self):
        payload = text = None
        message = self.md.get("message", {})
        if "text" in message:
            text = message.get("text")
        if "quick_reply" in message:
            qr = message.get("quick_reply", {})
            if "payload" in qr:
                payload = qr.get("payload")
        return (text, payload)

    def _process_request(self):
        """
        Populate self.reply and self.data
        """
        if self.request_type == FacebookAgent.REQ_MESSAGE:
            message, payload = self._get_fbook_message()
            action = parameters = None
            if payload:
                # Quick reply
                action = payload
            elif message:
                action, parameters = self.parse_message(message)
            if action:
                self.reply, self.message_data, end_convo = self.respond_to_action(
                    action, parameters=parameters
                )
        elif self.request_type == FacebookAgent.REQ_POSTBACK:
            payload = self.md.get("postback", {}).get("payload")
            self.reply, self.message_data, end_convo = self.respond_to_action(payload)
        elif self.request_type == FacebookAgent.REQ_ACCOUNT_LINK and self.user:
            self.reply = (
                "Alright %s, you've successfully connected with tyr!"
                % self.user.first_name()
            )
            self.message_data = self._quick_replies(
                [("Learn about tyr", "GET_STARTED")]
            )

    def handle_error(self, response):
        logging.warning(response.content)
        data = tools.getJson(response.content)
        error = data.get("error", {})
        code = error.get("code")
        subcode = error.get("error_subcode")
        if code == 190 and subcode == 460:
            # Error validating access token: The session has been invalidated because the user
            # changed their password or Facebook has changed the session for security reasons.
            pass

    def send_response(self):
        if self.fb_id and (self.reply or self.message_data):
            message_object = {}
            if self.reply and "attachment" not in self.message_data:
                message_object["text"] = self.reply
            if self.message_data:
                message_object.update(self.message_data)
            body = {"recipient": {"id": self.fb_id}, "message": message_object}
            logging.debug(body)
            url = (
                "https://graph.facebook.com/v2.6/me/messages?access_token=%s"
                % secrets.FB_ACCESS_TOKEN
            )
            if tools.on_dev_server():
                logging.debug("Not sending request, on dev")
            else:
                response = urlfetch.fetch(
                    url,
                    payload=json.dumps(body),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                logging.debug(response.status_code)
                if response.status_code != 200:
                    self.handle_error(response)
            return body
