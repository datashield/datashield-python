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
    password: your-password-here
  - name: server2
    url: https://opal.example.org
    token: your-access-token-here
    profile: default
  - name: server3
    url: https://study.example.org/opal
    user: dsuser
    password: your-password-here
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
        assert config.servers[0].password == "your-password-here"
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
        assert config.servers[2].password == "your-password-here"
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


def test_create_dslogininfo_requires_user_or_token():
    """Test that DSLoginInfo requires at least one credential method."""
    with pytest.raises(ValidationError) as exc_info:
        DSLoginInfo(name="test", url="https://example.org")

    assert "either user or token must be provided" in str(exc_info.value).lower()


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


def test_load_no_config_files(monkeypatch):
    """Test loading configuration when no config files exist."""
    # Mock the CONFIG_FILES to point to non-existent paths
    monkeypatch.setattr(
        "datashield.interface.CONFIG_FILES", ["/nonexistent/path/config.yaml", "/another/nonexistent/path/config.yaml"]
    )

    config = DSConfig.load()

    assert config is not None
    assert len(config.servers) == 0


def test_load_from_first_config_file(monkeypatch):
    """Test loading configuration from the first config file found."""
    yaml_content = """
servers:
  - name: server1
    url: https://example1.org
    user: user1
    password: pass1
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        first_config_file = f.name

    try:
        # Mock CONFIG_FILES to use our temporary file
        monkeypatch.setattr("datashield.interface.CONFIG_FILES", [first_config_file, "/nonexistent/second/config.yaml"])

        config = DSConfig.load()

        assert config is not None
        assert len(config.servers) == 1
        assert config.servers[0].name == "server1"
        assert config.servers[0].url == "https://example1.org"
        assert config.servers[0].user == "user1"

    finally:
        os.unlink(first_config_file)


def test_load_from_second_config_file(monkeypatch):
    """Test loading configuration from the second config file if first doesn't exist."""
    yaml_content = """
servers:
  - name: server2
    url: https://example2.org
    user: user2
    token: token123
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        second_config_file = f.name

    try:
        # Mock CONFIG_FILES to use our temporary file as second option
        monkeypatch.setattr("datashield.interface.CONFIG_FILES", ["/nonexistent/first/config.yaml", second_config_file])

        config = DSConfig.load()

        assert config is not None
        assert len(config.servers) == 1
        assert config.servers[0].name == "server2"
        assert config.servers[0].url == "https://example2.org"
        assert config.servers[0].token == "token123"

    finally:
        os.unlink(second_config_file)


def test_load_merge_multiple_config_files(monkeypatch):
    """Test merging configurations from multiple config files."""
    yaml_content1 = """
servers:
  - name: server1
    url: https://example1.org
    user: user1
    password: pass1
  - name: server2
    url: https://example2.org
    user: user2
    password: pass2
"""

    yaml_content2 = """
servers:
  - name: server2
    url: https://example2-updated.org
    user: user2_updated
    password: pass2_updated
  - name: server3
    url: https://example3.org
    token: token123
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f1:
        f1.write(yaml_content1)
        first_config_file = f1.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f2:
        f2.write(yaml_content2)
        second_config_file = f2.name

    try:
        # Mock CONFIG_FILES to use both our temporary files
        monkeypatch.setattr("datashield.interface.CONFIG_FILES", [first_config_file, second_config_file])

        config = DSConfig.load()

        assert config is not None
        assert len(config.servers) == 3

        # Check server1 (from first file, unchanged)
        server1 = next(s for s in config.servers if s.name == "server1")
        assert server1.url == "https://example1.org"
        assert server1.user == "user1"

        # Check server2 (from first file, but updated by second file)
        server2 = next(s for s in config.servers if s.name == "server2")
        assert server2.url == "https://example2-updated.org"
        assert server2.user == "user2_updated"
        assert server2.password == "pass2_updated"

        # Check server3 (from second file only)
        server3 = next(s for s in config.servers if s.name == "server3")
        assert server3.url == "https://example3.org"
        assert server3.token == "token123"

    finally:
        os.unlink(first_config_file)
        os.unlink(second_config_file)


def test_load_handles_invalid_yaml_silently(monkeypatch):
    """Test that load() silently handles invalid YAML files."""
    invalid_yaml_content = """
servers:
  - name: server1
    url: https://example.org
    invalid: yaml: content:
"""

    valid_yaml_content = """
servers:
  - name: server2
    url: https://example2.org
    user: user2
    password: pass2
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f1:
        f1.write(invalid_yaml_content)
        invalid_config_file = f1.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f2:
        f2.write(valid_yaml_content)
        valid_config_file = f2.name

    try:
        # Mock CONFIG_FILES with invalid file first, then valid file
        monkeypatch.setattr("datashield.interface.CONFIG_FILES", [invalid_config_file, valid_config_file])

        # Should not raise an exception, but load from the valid file
        config = DSConfig.load()

        assert config is not None
        assert len(config.servers) == 1
        assert config.servers[0].name == "server2"
        assert config.servers[0].url == "https://example2.org"

    finally:
        os.unlink(invalid_config_file)
        os.unlink(valid_config_file)


def test_load_handles_permission_denied_silently(monkeypatch):
    """Test that load() silently handles files without read permissions."""
    yaml_content1 = """
servers:
  - name: server1
    url: https://example1.org
    user: user1
    password: pass1
"""

    yaml_content2 = """
servers:
  - name: server2
    url: https://example2.org
    user: user2
    password: pass2
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f1:
        f1.write(yaml_content1)
        no_read_file = f1.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f2:
        f2.write(yaml_content2)
        readable_file = f2.name

    try:
        # Remove read permissions from first file
        os.chmod(no_read_file, 0o000)

        # Mock CONFIG_FILES with unreadable file first, then readable file
        monkeypatch.setattr("datashield.interface.CONFIG_FILES", [no_read_file, readable_file])

        # Should not raise an exception, but load from the readable file
        config = DSConfig.load()

        assert config is not None
        assert len(config.servers) == 1
        assert config.servers[0].name == "server2"
        assert config.servers[0].url == "https://example2.org"

    finally:
        # Restore permissions to allow cleanup
        os.chmod(no_read_file, 0o644)
        os.unlink(no_read_file)
        os.unlink(readable_file)
