"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler_test"


# Now we can import app

from app import app

app.app_context().push()

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

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

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User.query.get_or_404(1)
        u2 = User.query.get_or_404(2)

        # No messages & no followers and no following
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertFalse(u.is_following(u2))
        self.assertFalse(u.is_followed_by(u2))

        # Yes Followers or following another user
        msg = Message(text="test", user_id=1)
        u.following.append(u2)
        u2.following.append(u)
        u.messages.append(msg)
        db.session.commit()

        self.assertTrue(u.is_following(u2))
        self.assertTrue(u.is_followed_by(u2))
        self.assertEqual(len(u.messages), 1)
        self.assertEqual(len(u.followers), 1)

        # No likes
        self.assertEqual(len(u.likes), 0)

        # Yes likes
        u.likes.append(msg)
        db.session.commit()

        self.assertEqual(len(u.likes), 1)

        # Auth fails
        self.assertFalse(User.authenticate("Fred", u.password))
        self.assertFalse(User.authenticate(u.username, "Fred"))

        # Auth success
        self.assertTrue(User.authenticate(u.username, "HASHED_PASSWORD"))
