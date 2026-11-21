from datetime import date, datetime

from Backend.clock import FixedClock, day_key, next_month_start, slot_key
from Backend.services.auth import PasswordHasher


def test_keys_sort_like_time():
    assert day_key(date(2026, 11, 21)) == 20261121
    assert slot_key(datetime(2026, 11, 21, 14, 5)) == 2026112114
    assert slot_key(datetime(2026, 12, 1, 8)) > slot_key(datetime(2026, 11, 30, 16))


def test_next_month_start_wraps_the_year():
    assert next_month_start(date(2026, 12, 15)) == date(2027, 1, 1)
    assert next_month_start(date(2026, 1, 31)) == date(2026, 2, 1)


def test_fixed_clock_stands_still():
    clock = FixedClock(datetime(2026, 5, 6, 7, 8))
    assert clock.today() == date(2026, 5, 6) and clock.now().hour == 7


def test_password_hasher_roundtrip():
    hasher = PasswordHasher(rounds=1000)
    hashed = hasher.hash("secret")
    assert hasher.verify("secret", hashed) and not hasher.verify("other", hashed)
    assert not hasher.verify("secret", "not a hash")
