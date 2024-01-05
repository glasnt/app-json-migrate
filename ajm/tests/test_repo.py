import pytest


from repo import _parse_url


@pytest.mark.parametrize(
    "data, expected",
    [
        ("https://github.com/GoogleCloudPlatform/devrel-demos/tree/main/app-dev/ruby-frameworks-cloudrun/sinatra-webrick",
          ("GoogleCloudPlatform/devrel-demos", "main", "app-dev/ruby-frameworks-cloudrun/sinatra-webrick"))
    ]
)
def test_parse_url(data, expected):
    assert _parse_url(data) == expected
