"""User message tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, datetime

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


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        for i in range(5):
            db.session.add(
                User.signup(
                    email=f"test@test.com{i+1}",
                    username=f"testuser{i+1}",
                    password="HASHED_PASSWORD",
                    image_url="none",
                )
            )

        db.session.commit()

        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""

        # No messages
        self.assertFalse(Message.query.get(1))

        # Yes Messages
        timestamp = datetime(1968, 4, 2, 0, 0)
        text = "test"
        user_id = 1

        msg = Message(text=text, user_id=user_id, timestamp=timestamp)

        db.session.add(msg)
        db.session.commit()

        self.assertTrue(Message.query.get(1))

        # Verify message data and relationships
        self.assertTrue(msg.id == 1)
        self.assertFalse(msg.id == 2)

        self.assertTrue(msg.user_id == msg.user.id)
        self.assertFalse(msg.user_id == 2)

        self.assertTrue(msg.timestamp == timestamp)
        self.assertFalse(msg.timestamp == datetime(1968, 4, 2, 0, 1))

        self.assertTrue(msg.text == text)
        self.assertFalse(msg.text == "1")
