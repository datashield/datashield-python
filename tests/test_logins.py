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
    try:
        DSLoginBuilder().add(None, "https://opal-demo.obba.org", "dsuser", "P@ssw0rd")
        raise ValueError("Expected ValueError for missing name") from None
    except ValueError:
        assert True
    # url not missing
    try:
        DSLoginBuilder().add("server1", None, "dsuser", "P@ssw0rd")
        raise ValueError("Expected ValueError for missing URL") from None
    except ValueError:
        assert True
    # name is unique
    try:
        DSLoginBuilder().add("server1", "https://opal-demo.obba.org", "dsuser", "P@ssw0rd").add(
            "server1", "https://demo.datashield.org", token="1234abcd"
        )
        raise ValueError("Expected ValueError for duplicate server name") from None
    except ValueError:
        assert True
    # either user and token is missing
    try:
        DSLoginBuilder().add("server1", "https://opal-demo.obba.org").add("server2", "https://demo.datashield.org")
        raise ValueError("Expected ValueError for missing credentials") from None
    except ValueError:
        assert True
