"""
Test loading configuration from YAML file using Pydantic.
"""

import os
import tempfile
import pytest
from pydantic import ValidationError
from datashield import DSConfig, DSLoginInfo


def test_load_config_from_yaml():
    """Test loading a configuration from a YAML file."""
    yaml_content = """
servers:
  - name: server1
    url: https://opal-demo.obiba.org
    user: dsuser
    password: P@ssw0rd
  - name: server2
    url: https://opal.example.org
    token: your-access-token-here
    profile: default
  - name: server3
    url: https://study.example.org/opal
    user: dsuser
    password: P@ssw0rd
    profile: custom
    driver: datashield_opal.OpalDriver
"""

    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_file = f.name

    try:
        # Load the configuration
        config = DSConfig.load_from_file(temp_file)

        # Verify the configuration
        assert config is not None
        assert len(config.servers) == 3

        # Check server1
        assert config.servers[0].name == "server1"
        assert config.servers[0].url == "https://opal-demo.obiba.org"
        assert config.servers[0].user == "dsuser"
        assert config.servers[0].password == "P@ssw0rd"
        assert config.servers[0].token is None
        assert config.servers[0].profile == "default"
        assert config.servers[0].driver == "datashield_opal.OpalDriver"

        # Check server2
        assert config.servers[1].name == "server2"
        assert config.servers[1].url == "https://opal.example.org"
        assert config.servers[1].user is None
        assert config.servers[1].password is None
        assert config.servers[1].token == "your-access-token-here"
        assert config.servers[1].profile == "default"
        assert config.servers[1].driver == "datashield_opal.OpalDriver"

        # Check server3
        assert config.servers[2].name == "server3"
        assert config.servers[2].url == "https://study.example.org/opal"
        assert config.servers[2].user == "dsuser"
        assert config.servers[2].password == "P@ssw0rd"
        assert config.servers[2].token is None
        assert config.servers[2].profile == "custom"
        assert config.servers[2].driver == "datashield_opal.OpalDriver"

    finally:
        # Clean up
        os.unlink(temp_file)


def test_load_config_with_defaults():
    """Test that default values are applied when not specified in YAML."""
    yaml_content = """
servers:
  - name: minimal
    url: https://example.org
    user: testuser
    password: testpass
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_file = f.name

    try:
        config = DSConfig.load_from_file(temp_file)

        assert config is not None
        assert len(config.servers) == 1
        assert config.servers[0].name == "minimal"
        assert config.servers[0].url == "https://example.org"
        assert config.servers[0].user == "testuser"
        assert config.servers[0].password == "testpass"
        assert config.servers[0].profile == "default"
        assert config.servers[0].driver == "datashield_opal.OpalDriver"

    finally:
        os.unlink(temp_file)


def test_load_empty_config():
    """Test loading an empty configuration file."""
    yaml_content = ""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_file = f.name

    try:
        config = DSConfig.load_from_file(temp_file)

        assert config is not None
        assert len(config.servers) == 0

    finally:
        os.unlink(temp_file)


def test_load_config_no_servers():
    """Test loading a configuration file without a 'servers' key."""
    yaml_content = """
other_key: value
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_file = f.name

    try:
        # This should raise a validation error because 'other_key' is not allowed
        with pytest.raises(ValidationError) as exc_info:
            DSConfig.load_from_file(temp_file)

        # Check that the error is about extra fields
        assert "extra" in str(exc_info.value).lower() or "forbidden" in str(exc_info.value).lower()

    finally:
        os.unlink(temp_file)


def test_pydantic_validation_missing_required_fields():
    """Test that Pydantic validates required fields."""
    yaml_content = """
servers:
  - name: incomplete
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_file = f.name

    try:
        # Should raise validation error for missing 'url' field
        with pytest.raises(ValidationError) as exc_info:
            DSConfig.load_from_file(temp_file)

        # Check that the error mentions the missing field
        assert "url" in str(exc_info.value).lower()

    finally:
        os.unlink(temp_file)


def test_create_dslogininfo_directly():
    """Test creating DSLoginInfo objects directly with Pydantic."""
    login = DSLoginInfo(name="test", url="https://example.org", user="testuser", password="testpass")

    assert login.name == "test"
    assert login.url == "https://example.org"
    assert login.user == "testuser"
    assert login.password == "testpass"
    assert login.profile == "default"
    assert login.driver == "datashield_opal.OpalDriver"


def test_create_dsconfig_directly():
    """Test creating DSConfig objects directly with Pydantic."""
    login1 = DSLoginInfo(name="server1", url="https://example1.org", user="user1", password="pass1")
    login2 = DSLoginInfo(name="server2", url="https://example2.org", token="token123")

    config = DSConfig(servers=[login1, login2])

    assert len(config.servers) == 2
    assert config.servers[0].name == "server1"
    assert config.servers[1].name == "server2"


def test_pydantic_extra_fields_forbidden():
    """Test that extra fields in server configuration are rejected."""
    yaml_content = """
servers:
  - name: server1
    url: https://example.org
    user: testuser
    password: testpass
    extra_field: should_fail
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        temp_file = f.name

    try:
        # Should raise validation error for extra field
        with pytest.raises(ValidationError) as exc_info:
            DSConfig.load_from_file(temp_file)

        assert "extra_field" in str(exc_info.value).lower() or "extra" in str(exc_info.value).lower()

    finally:
        os.unlink(temp_file)


def test_model_serialization():
    """Test that Pydantic models can be serialized to dict."""
    login = DSLoginInfo(name="test", url="https://example.org", user="testuser", password="testpass")

    # Test model_dump (Pydantic v2 method)
    data = login.model_dump()
    assert data["name"] == "test"
    assert data["url"] == "https://example.org"
    assert data["user"] == "testuser"
    assert data["password"] == "testpass"
    assert data["profile"] == "default"
    assert data["driver"] == "datashield_opal.OpalDriver"
