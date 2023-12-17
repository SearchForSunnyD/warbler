"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY

app.app_context().push()

# Create our tables and users (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

for i in range(5):
    db.session.add(
        User.signup(
            email=f"test@test.com{i+1}",
            username=f"testuser{i+1}",
            password="HASHED_PASSWORD",
            image_url=None,
        )
    )

db.session.commit()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config["WTF_CSRF_ENABLED"] = False


class UserViewTestCase(TestCase):
    def setUp(self):
        self.client = app.test_client()

    def login(self, client, username, password):
        return client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_list_users(self):
        with self.client as client:
            response = client.get("/users")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"testuser1", response.data)

    def test_users_show(self):
        with self.client as client:
            response = client.get("/users/1")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"testuser1", response.data)

    def test_show_following(self):
        with self.client as client:
            self.login(client, "testuser1", "HASHED_PASSWORD")

            response = client.get("/users/1/following")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"testuser1", response.data)

    def test_profile_authenticated(self):
        with self.client as client:
            self.login(client, "testuser1", "HASHED_PASSWORD")

            response = client.get("/users/profile")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Edit Your Profile", response.data)

    def test_profile_unauthenticated(self):
        with self.client as client:
            response = client.get("/users/profile", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Access unauthorized", response.data)

    def test_add_follow(self):
        with self.client as client:
            self.login(client, "testuser1", "HASHED_PASSWORD")

            response = client.post("/users/follow/2", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"testuser2", response.data)
