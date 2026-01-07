"""test user"""

from shared.user import User


def test_user():
    """test user"""
    user = User(
        id=1,
        username="username",
        email="email",
        first_name="first_name",
        last_name="last_name",
        password="password",
    )
    assert user.id == 1
    assert user.username == "username"
    assert user.email == "email"
    assert user.first_name == "first_name"
    assert user.last_name == "last_name"
    assert user.password == "password"
