from datashield.utils import DSLoginBuilder

def test_logins():
    builder = DSLoginBuilder().add("server1", "https://opal-demo.obba.org", "dsuser", "P@ssw0rd").add("server2", "https://demo.datashield.org", token = "1234abcd")
    logins = builder.build()
    assert len(logins) == 2
    assert logins[0]["name"] == "server1"
    assert logins[0]["user"] is not None
    assert logins[0]["password"] is not None
    assert logins[0]["token"] is None
    assert logins[1]["name"] == "server2"
    assert logins[1]["user"] is None
    assert logins[1]["password"] is None
    assert logins[1]["token"] is not None