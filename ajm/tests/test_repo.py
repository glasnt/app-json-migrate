import pytest


from repo import _parse_url


@pytest.mark.parametrize(
    "data, expected",
    [   ("https://github.com/GoogleCloudPlatform/devrel-demos", ("GoogleCloudPlatform/devrel-demos", "main", "/")),
        ("https://github.com/GoogleCloudPlatform/devrel-demos/tree/main/app-dev/ruby-frameworks-cloudrun/sinatra-webrick",
          ("GoogleCloudPlatform/devrel-demos", "main", "app-dev/ruby-frameworks-cloudrun/sinatra-webrick")),

    ]
)
def test_parse_url(data, expected):
    repo, branch, directory = _parse_url(data)
    assert repo.full_name == expected[0]
    assert branch == expected[1]
    assert directory == expected[2]
