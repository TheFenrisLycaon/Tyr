#!/usr/bin/python
# -*- coding: utf8 -*-

from datetime import date, datetime

from utils import tools

from constants.constants import REPORT
from controllers.main import app as tst_app
from models.models import (Goal, Habit, HabitDay, MiniJournal, Project, Report,
                           Task)

from .base_test_case import BaseTestCase

DATE_FMT = "%Y-%m-%d %H:%M:%S %Z"


class ReportsTestCases(BaseTestCase):
    def setUp(self):
        self.set_application(tst_app)
        self.setup_testbed()
        self.init_standard_stubs()
        self.init_app_basics()
        self.u = self.users[0]

    def _test_report(self, params, expected_output):
        response = self.post_json(
            "/api/report/generate", params, headers=self.api_headers
        )
        rid = response.get("report", {}).get("id")
        self.execute_tasks_until_empty()
        response = self.get("/api/report/serve?rid=%s" % rid, headers=self.api_headers)
        compare_output = response.body  # Avoid whitespace normalization in normal_body
        compare_output = (
            compare_output.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        )
        self.assertEqual(
            [x for x in compare_output if x], [",".join(eo) for eo in expected_output]
        )
        self.assertEqual(response.content_type, "text/csv")
        report = self.u.get(Report, rid)
        self.assertTrue(report.is_done())
        self.assertTrue(report.get_duration() > 0)

    def test_task_report(self):
        due_date = datetime(2017, 10, 2, 12, 0)
        task = Task.Create(self.u, "New task", due=due_date)
        task.put()

        self._test_report(
            {"type": REPORT.TASK_REPORT},
            [
                [
                    "Date Created",
                    "Date Due",
                    "Date Done",
                    "Title",
                    "Done",
                    "Archived",
                    "Seconds Logged",
                    "Complete Sessions Logged",
                ],
                [
                    tools.sdatetime(task.dt_created, fmt=DATE_FMT),
                    "2017-10-02 12:00:00 UTC",
                    "N/A",
                    "New task",
                    "0",
                    "0",
                    "0",
                    "0",
                ],
            ],
        )

    def test_goal_report(self):
        g = Goal.Create(self.u, "2017")
        g.Update(text=["Goal 1", "Goal 2"], assessments=[3, 4])
        g.put()

        self._test_report(
            {"type": REPORT.GOAL_REPORT},
            [
                [
                    "Goal Period",
                    "Date Created",
                    "Text 1",
                    "Text 2",
                    "Text 3",
                    "Text 4",
                    "Goal Assessments",
                    "Overall Assessment",
                ],
                [
                    "2017",
                    tools.sdatetime(g.dt_created, fmt="%Y-%m-%d %H:%M:%S %Z"),
                    "Goal 1",
                    "Goal 2",
                    "",
                    "",
                    '"3,4"',
                    "3.5",
                ],
            ],
        )

    def test_journal_report(self):
        jrnl = MiniJournal.Create(self.u, date=date(2017, 4, 5))
        jrnl.Update(lat="-1.289744", lon="36.7694933", tags=[], data={"happiness": 9})
        jrnl.put()

        self._test_report(
            {"type": REPORT.JOURNAL_REPORT},
            [
                ["Date", "Tags", "Location", "Data"],
                ["2017-04-05", "", '"-1.289744,36.7694933"', '"{""happiness"": 9}"'],
            ],
        )

    def test_habit_report(self):
        habit_run = Habit.Create(self.u)
        habit_run.Update(name="Run")
        habit_run.put()
        marked_done, hd = HabitDay.Toggle(habit_run, datetime.today())

        self._test_report(
            {"type": REPORT.HABIT_REPORT},
            [
                ["Created", "Updated", "Date", "Habit", "Done", "Committed"],
                [
                    tools.sdatetime(hd.dt_created, fmt="%Y-%m-%d %H:%M:%S %Z"),
                    tools.sdatetime(hd.dt_updated, fmt="%Y-%m-%d %H:%M:%S %Z"),
                    tools.iso_date(datetime.now()),
                    "Run",
                    "1",
                    "0",
                ],
            ],
        )

    def test_project_report(self):
        prj = Project.Create(self.u)
        prj.Update(
            title="New Project", subhead="Project subhead", due=datetime(2017, 4, 5)
        )
        prj.set_progress(3)
        prj.put()

        self._test_report(
            {"type": REPORT.PROJECT_REPORT},
            [
                [
                    "Date Created",
                    "Date Due",
                    "Date Completed",
                    "Date Archived",
                    "Title",
                    "Subhead",
                    "Links",
                    "Starred",
                    "Archived",
                    "Progress",
                    "Progress 10%",
                    "Progress 20%",
                    "Progress 30%",
                    "Progress 40%",
                    "Progress 50%",
                    "Progress 60%",
                    "Progress 70%",
                    "Progress 80%",
                    "Progress 90%",
                    "Progress 100%",
                ],
                [
                    tools.sdatetime(prj.dt_created, fmt="%Y-%m-%d %H:%M:%S %Z"),
                    tools.sdatetime(prj.dt_due, fmt="%Y-%m-%d %H:%M:%S %Z"),
                    tools.sdatetime(prj.dt_completed, fmt="%Y-%m-%d %H:%M:%S %Z"),
                    tools.sdatetime(prj.dt_archived, fmt="%Y-%m-%d %H:%M:%S %Z"),
                    "New Project",
                    "Project subhead",
                    "",
                    "0",
                    "0",
                    "30%",
                    "N/A",
                    "N/A",
                    tools.sdatetime(
                        tools.dt_from_ts(prj.progress_ts[2]), fmt="%Y-%m-%d %H:%M:%S %Z"
                    ),
                    "N/A",
                    "N/A",
                    "N/A",
                    "N/A",
                    "N/A",
                    "N/A",
                    "N/A",
                ],
            ],
        )

    def test_fetch_and_delete(self):
        self.post_json(
            "/api/report/generate",
            {"type": REPORT.TASK_REPORT},
            headers=self.api_headers,
        )
        self.execute_tasks_until_empty()
        reports = Report.Fetch(self.u)
        self.assertEqual(len(reports), 1)
        # Delete
        reports[0].clean_delete()
        reports = Report.Fetch(self.u)
        self.assertEqual(len(reports), 0)
