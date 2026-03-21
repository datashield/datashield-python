from datashield import DSSession


class FakeResult:
    def __init__(self, value):
        self.value = value

    def is_completed(self) -> bool:
        return True

    def fetch(self):
        return self.value


class FakeConn:
    def __init__(self, name: str):
        self._name = name
        self.started = False
        self.disconnected = False
        self.saved_workspaces = []
        self.restored_workspaces = []
        self.removed_workspaces = []
        self.rm_symbols = []
        self.assign_expr_calls = []
        self.keep_alive_calls = 0

    def get_name(self) -> str:
        return self._name

    def list_tables(self) -> list:
        return [f"{self._name}_table"]

    def has_session(self) -> bool:
        return self.started

    def start_session(self, asynchronous: bool = True):
        self.started = True
        return {"started": True, "async": asynchronous}

    def is_session_started(self) -> bool:
        return self.started

    def get_session(self):
        return {"name": self._name}

    def list_symbols(self) -> list:
        return [f"{self._name}_symbol"]

    def rm_symbol(self, name: str) -> None:
        self.rm_symbols.append(name)

    def assign_expr(self, symbol: str, expr: str, asynchronous: bool = True) -> FakeResult:
        self.assign_expr_calls.append((symbol, expr, asynchronous))
        return FakeResult({"symbol": symbol, "expr": expr, "conn": self._name})

    def aggregate(self, expr: str, asynchronous: bool = True) -> FakeResult:
        return FakeResult({"expr": expr, "conn": self._name, "async": asynchronous})

    def save_workspace(self, name: str) -> list:
        self.saved_workspaces.append(name)
        return self.saved_workspaces

    def restore_workspace(self, name: str) -> list:
        self.restored_workspaces.append(name)
        return self.restored_workspaces

    def rm_workspace(self, name: str) -> list:
        self.removed_workspaces.append(name)
        return self.removed_workspaces

    def keep_alive(self) -> None:
        self.keep_alive_calls += 1

    def disconnect(self) -> None:
        self.disconnected = True


def make_session() -> tuple[DSSession, FakeConn, FakeConn]:
    conn1 = FakeConn("server1")
    conn2 = FakeConn("server2")
    session = DSSession([])
    session.conns = [conn1, conn2]
    session.errors = {}
    return session, conn1, conn2


def test_tables_filters_connections():
    session, _, _ = make_session()

    result = session.tables(conn_names=["server2", "unknown"])

    assert result == {"server2": ["server2_table"]}


def test_assign_expr_filters_connections():
    session, conn1, conn2 = make_session()

    session.assign_expr("x", "1+1", conn_names=["server1", "unknown"])

    assert conn1.assign_expr_calls == [("x", "1+1", True)]
    assert conn2.assign_expr_calls == []


def test_aggregate_filters_connections():
    session, conn1, conn2 = make_session()

    result = session.aggregate("2+2", conn_names=["server2"])

    assert result == {"server2": {"expr": "2+2", "conn": "server2", "async": True}}
    assert conn1.assign_expr_calls == []
    assert conn2.assign_expr_calls == []


def test_workspace_methods_filter_connections():
    session, conn1, conn2 = make_session()

    session.workspace_save("wk", conn_names=["server1"])
    session.workspace_restore("wk", conn_names=["server2"])
    session.workspace_rm("wk", conn_names=["server2", "missing"])

    assert conn1.saved_workspaces == ["server1:wk"]
    assert conn2.saved_workspaces == []
    assert conn1.restored_workspaces == []
    assert conn2.restored_workspaces == ["server2:wk"]
    assert conn1.removed_workspaces == []
    assert conn2.removed_workspaces == ["server2:wk"]


def test_close_filters_connections_and_keeps_others_open():
    session, conn1, conn2 = make_session()

    session.close(conn_names=["server1", "unknown"])

    assert conn1.disconnected is True
    assert conn2.disconnected is False
    assert session.get_connection_names() == ["server2"]
