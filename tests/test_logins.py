import pytest
from datashield import DSLoginBuilder


def test_logins():
    builder = (
        DSLoginBuilder()
        .add("server1", "https://opal-demo.obba.org", "dsuser", "P@ssw0rd")
        .add("server2", "https://demo.datashield.org", token="1234abcd", profile="omics")
    )
    logins = builder.build()
    assert len(logins) == 2
    assert logins[0].name == "server1"
    assert logins[0].user is not None
    assert logins[0].password is not None
    assert logins[0].token is None
    assert logins[0].profile == "default"
    assert logins[0].driver == "datashield_opal.OpalDriver"
    assert logins[1].name == "server2"
    assert logins[1].user is None
    assert logins[1].password is None
    assert logins[1].token is not None
    assert logins[1].profile == "omics"
    builder.remove("server1")
    logins = builder.build()
    assert len(logins) == 1
    assert logins[0].name == "server2"


def test_login_validations():
    # name not missing
    with pytest.raises(ValueError, match="Server name is missing"):
        DSLoginBuilder().add(None, "https://opal-demo.obba.org", "dsuser", "P@ssw0rd")

    # url not missing
    with pytest.raises(ValueError, match="Server URL is missing"):
        DSLoginBuilder().add("server1", None, "dsuser", "P@ssw0rd")

    # name is unique
    with pytest.raises(ValueError, match="Server name must be unique"):
        DSLoginBuilder().add("server1", "https://opal-demo.obba.org", "dsuser", "P@ssw0rd").add(
            "server1", "https://demo.datashield.org", token="1234abcd"
        )

    # either user and token is missing
    with pytest.raises(ValueError, match="Either user or token must be provided"):
        DSLoginBuilder().add("server1", "https://opal-demo.obba.org").add("server2", "https://demo.datashield.org")
