from __future__ import division

__copyright__ = "Copyright (C) 2014 Andreas Kloeckner"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import shutil
from django.test import TestCase, Client
from django.urls import resolve, reverse
from accounts.models import User
from course.models import FlowSession, Course, GradingOpportunity #, Participation



class GradeTest(TestCase):
    # @classmethod
    # def setUpClass(cls):
    #     super(GradeTest, cls).setUpClass()
    #     cls.modify_settings(EMAIL_BACKEND=
    #                     'django.core.mail.backends.console.EmailBackend')

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        # Admin account
        cls.admin = User.objects.create_superuser(
                username="testadmin",
                password="test",
                email="test@example.com",
                first_name="Test",
                last_name="Admin")
        cls.admin.save()

        # User account
        # cls.user1 = User.objects.create_user(
        #         username="tester1",
        #         password="test",
        #         email="tester1@example.com",
        #         first_name="Test1",
        #         last_name="Tester")
        # cls.user1.save()
        #
        # cls.user2 = User.objects.create_user(
        #         username="tester2",
        #         password="test",
        #         email="tester2@example.com",
        #         first_name="Test2",
        #         last_name="Tester")
        # cls.user2.save()

        # Create the course here and check later to
        # avoid exceptions raised here
        cls.c = Client()
        cls.c.login(
            username="testadmin",
            password="test")
        cls.c.post("/new-course/", dict(
            identifier="test-course",
            name="Test Course",
            number="CS123",
            time_period="Fall 2016",
            hidden=False,
            listed=True,
            accepts_enrollment=True,
            git_source="git://github.com/inducer/relate-sample",
            course_file="course.yml",
            events_file="events.yml",
            enrollment_approval_required=False,
            enrollment_required_email_suffix=None,
            from_email="inform@tiker.net",
            notify_email="inform@tiker.net"))

        # Some classwise sharing data
        cls.datas = {"course_identifier": "test-course", "flow_id": "quiz-test"}
        cls.datas["flow_session_id"] = []

        # Make sure admin is logged in after all this
        # cls.do_quiz(cls.user1)
        # cls.do_quiz(cls.user2)
        cls.do_quiz(cls.admin)

    @classmethod
    def tearDownClass(cls):
        # Remove created folder
        shutil.rmtree('../' + cls.datas["course_identifier"])
        super(GradeTest, cls).tearDownClass()

    # Use specified user to take a quiz
    @classmethod
    def do_quiz(cls, user):
        # Login user first
        cls.c.logout()
        cls.c.login(
                    username=user.username,
                    password="test")

        # Enroll if not admin
        # Little hacky for not using enrollment view
        # if not user.is_superuser:
        #     participation = Participation()
        #     participation.user = user
        #     participation.course = Course.objects.filter(identifier=
        #                                                     "test-course")[0]
        #     participation.status = "active"
        #     participation.save()

        params = cls.datas.copy()
        del params["flow_session_id"]
        resp = cls.c.post(reverse("relate-view_start_flow", kwargs=params))

        # Yep, no regax!
        _, _, kwargs = resolve(resp.url)
        # Store flow_session_id
        cls.datas["flow_session_id"].append(kwargs["flow_session_id"])

        # Let it raise error
        # Use pop() will not
        del kwargs["ordinal"]
        resp = cls.c.post(reverse("relate-finish_flow_session_view",
                                kwargs=kwargs), {'submit': ['']})
