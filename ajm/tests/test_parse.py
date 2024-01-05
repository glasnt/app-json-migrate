import pytest

from parse import _fix_service_name


@pytest.mark.parametrize(
    "data, expected",
    [
        ("my-service", "my-service"),
        ("my_service-", "my-service"),
        ("-my_service", "srv-my-service"),
        (
            "my-very-very-very-verylong-file-that-is-long-verylong-verylong-verylong-verylong-verylong-verylong-",
            "my-very-very-very-verylong-file-that-is-long-verylong-verylong",
        ),
    ],
)
def test_fix_service_name(data, expected):
    assert _fix_service_name(data) == expected
