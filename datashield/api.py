"""
DataSHIELD API.
"""

from datashield.interface import DSLoginInfo, DSConnection, DSDriver, DSError
import time


class DSLoginBuilder:
    """
    Helper class to formalize DataSHIELD login arguments for a set of servers.
    """

    def __init__(self):
        self.items: list[DSLoginInfo] = []

    def add(
        self,
        name: str,
        url: str,
        user: str = None,
        password: str = None,
        token: str = None,
        profile: str = "default",
        driver: str = "datashield_opal.OpalDriver",
    ):
        """
        Add DataSHIELD login information.

        :param name: The name of the server, must be unique
        :param url: The URL of the server
        :param user: The user name (required if token is None)
        :param password: The user password
        :param token: The access token (required if user is None)
        :param profile: The DataSHIELD profile name to be used
        :param driver: The DataSHIELD connection driver class full name
        :return Itself
        """
        if name is None:
            raise ValueError("Server name is missing")
        if url is None:
            raise ValueError("Server URL is missing")
        found = [x for x in self.items if x.name == name]
        if len(found) > 0:
            raise ValueError(f"Server name must be unique: {name}")
        if user is None and token is None:
            raise ValueError("Either user or token must be provided")
        self.items.append(DSLoginInfo(name, url, user, password, token, profile, driver))
        return self

    def remove(self, name: str):
        """
        Remove the DataSHIELD login information by its name, if it exists.

        :param name: The name of the server to remove
        :return Itself
        """
        self.items = [x for x in self.items if x.name != name]
        return self

    def build(self) -> list[DSLoginInfo]:
        """
        Get the list of DataSHIELD login info.

        :return The list of DSLoginInfo objects
        """
        return self.items


class DSSession:
    """
    DataSHIELD session, establishes connections with remote servers and performs commands.
    """

    def __init__(self, logins: list[DSLoginInfo]):
        """
        Create a session, with connection information. Does not open the connections.

        :param logins: A list of login details
        """
        self.logins = logins
        self.conns: list[DSConnection] = None
        self.errors: dict = None

    def open(self, restore: str = None, failSafe: bool = False) -> None:
        """
        Open connections with remote servers from provided login details.

        :param restore: The workspace name to be restored
        """
        self.conns = []
        self.errors = {}
        for info in self.logins:
            try:
                driver = DSDriver.load_class(info.driver)
                conn = driver.new_connection(info, restore=restore)
                self.conns.append(conn)
            except Exception as e:
                if failSafe:
                    self.errors[info.name] = e
                else:
                    # close other connections before raising error
                    self.close()
                    raise e
        if self.has_errors():
            for name in self.errors:
                print(f"Connection to {name} has failed")

    def close(self, save: str = None) -> None:
        """
        Close connections with remote servers.

        :param cons: The list of connections to close.
        :param save: The name of the workspace to save before closing the connections.
        """
        self.errors = {}
        for conn in self.conns:
            try:
                if save:
                    conn.save_workspace(f"{conn.name}:{save}")
                conn.disconnect()
            except DSError:
                # silently fail
                pass
        self.conns = None

    def has_connections(self) -> bool:
        """
        Check if some connections were opened.

        :return: True if some connections were opened, False otherwise
        """
        return len(self.conns) > 0

    def get_connection_names(self) -> list[str]:
        """
        Get the opened connection names.

        :return: The list of opened connection names
        """
        if self.conns:
            return [conn.name for conn in self.conns]
        else:
            return []

    def has_errors(self) -> bool:
        """
        Check if last command execution has produced errors.

        :return: True if last command execution has produced errors, False otherwise
        """
        return len(self.errors) > 0

    def get_errors(self) -> dict:
        """
        Get the last command execution errors, per remote server name.

        :return: The last command execution errors, per remote server name
        """
        return self.errors

    #
    # Environment
    #

    def tables(self) -> dict:
        """
        List available table names from the data repository.

        :return: The available table names from the data repository, per remote server name
        """
        rval = {}
        for conn in self.conns:
            rval[conn.name] = conn.list_tables()
        return rval

    def resources(self) -> dict:
        """
        List available resource names from the data repository.

        :return: The available resource names from the data repository, per remote server name
        """
        rval = {}
        for conn in self.conns:
            rval[conn.name] = conn.list_resources()
        return rval

    def profiles(self) -> dict:
        """
        List available DataSHIELD profile names in the data repository.

        :return: The available DataSHIELD profile names in the data repository, per remote server name
        """
        rval = {}
        for conn in self.conns:
            rval[conn.name] = conn.list_profiles()
        return rval

    def packages(self) -> dict:
        """
        Get the list of DataSHIELD packages with their version, that have been configured on the remote data repository.

        :return: The list of DataSHIELD packages with their version, that have been configured on the remote data repository, per remote server name
        """
        rval = {}
        for conn in self.conns:
            rval[conn.name] = conn.list_packages()
        return rval

    def methods(self, type: str = "aggregate") -> dict:
        """
        Get the list of DataSHIELD methods that have been configured on the remote data repository.

        :param type: The type of method, either "aggregate" (default) or "assign"
        :return: The list of DataSHIELD methods that have been configured on the remote data repository, per remote server name
        """
        rval = {}
        for conn in self.conns:
            rval[conn.name] = conn.list_methods(type)
        return rval

    #
    # Workspaces
    #

    def workspaces(self) -> dict:
        """
        Get the list of DataSHIELD workspaces, that have been saved on the remote data repository.

        :return: The list of DataSHIELD workspaces, that have been saved on the remote data repository, per remote server name
        """
        rval = {}
        for conn in self.conns:
            rval[conn.name] = conn.list_workspaces()
        return rval

    def workspace_save(self, name: str) -> dict:
        """
        Save the DataSHIELD R session in a workspace on the remote data repository.

        :param name: The name of the workspace
        :return: The list of DataSHIELD workspaces, that have been saved on the remote data repository after saving the workspace, per remote server name
        """
        for conn in self.conns:
            conn.save_workspace(f"{conn.name}:{name}")
        return self.workspaces()

    def workspace_restore(self, name: str) -> dict:
        """
        Restore a saved DataSHIELD R session from the remote data repository. When restoring a workspace,
        any existing symbol or file with same name will be overridden.

        :param name: The name of the workspace
        :return: The list of DataSHIELD workspaces, that have been saved on the remote data repository after restoring the workspace, per remote server name
        """
        for conn in self.conns:
            conn.restore_workspace(f"{conn.name}:{name}")
        return self.workspaces()

    def workspace_rm(self, name: str) -> dict:
        """
        Remove a DataSHIELD workspace from the remote data repository. Ignored if no
        such workspace exists.

        :param name: The name of the workspace
        :return: The list of DataSHIELD workspaces, that have been saved on the remote data repository after removing the workspace, per remote server name
        """
        for conn in self.conns:
            conn.rm_workspace(f"{conn.name}:{name}")
        return self.workspaces()

    #
    # R session
    #

    def sessions(self) -> dict:
        """
        Ensure R sessions are started on the remote servers and get their information.

        :return: The R session information, per remote server name
        """
        rval = {}
        for conn in self.conns:
            if not conn.has_session():
                conn.start_session(asynchronous=True)
        # check for session status and wait until all are complete
        while any(conn.get_session().is_pending() for conn in self.conns):
            time.sleep(0.1)
        for conn in self.conns:
            rval[conn.name] = conn.get_session()
        self._check_errors()
        return rval

    def ls(self) -> dict:
        """
        After assignments have been performed, list the symbols that live in the DataSHIELD R session on the server side.

        :return: The symbols that live in the DataSHIELD R session on the server side, per remote server name
        """
        self._init_errors()
        self.sessions()  # ensure sessions are started and available
        rval = {}
        for conn in self.conns:
            try:
                rval[conn.name] = conn.list_symbols()
            except Exception as e:
                self._append_error(conn, e)
                rval[conn.name] = None
        self._check_errors()
        return rval

    def rm(self, symbol: str) -> None:
        """
        Remove a symbol from remote servers.

        :param symbol: The name of the symbol to remove
        """
        self._init_errors()
        self.sessions()  # ensure sessions are started and available
        for conn in self.conns:
            try:
                conn.rm_symbol(symbol)
            except Exception as e:
                self._append_error(conn, e)
        self._check_errors()

    def assign_table(
        self,
        symbol: str,
        table: str = None,
        tables: dict = None,
        variables: list = None,
        missings: bool = False,
        identifiers: str = None,
        id_name: str = None,
        asynchronous: bool = True,
    ) -> None:
        """
        Assign a data table from the data repository to a symbol in the DataSHIELD R session.

        :param symbol: The name of the destination symbol
        :param table: The default name of the table to assign
        :param tables: The name of the table to assign, per server name. If not defined, 'table' is used.
        :param asynchronous: Whether the operation is asynchronous (if supported by the DataSHIELD server)
        """
        self._init_errors()
        self.sessions()  # ensure sessions are started and available
        cmd = {}
        for conn in self.conns:
            name = table
            if tables and conn.name in tables:
                name = tables[conn.name]
            if name:
                try:
                    res = conn.assign_table(symbol, name, variables, missings, identifiers, id_name, asynchronous)
                    cmd[conn.name] = res
                except Exception as e:
                    self._append_error(conn, e)
        self._do_wait(cmd)
        self._check_errors()

    def assign_resource(
        self, symbol: str, resource: str = None, resources: dict = None, asynchronous: bool = True
    ) -> None:
        """
        Assign a resource from the data repository to a symbol in the DataSHIELD R session.

        :param symbol: The name of the destination symbol
        :param resource: The default name of the resource to assign
        :param resources: The name of the resource to assign, per server name. If not defined, 'resource' is used.
        :param asynchronous: Whether the operation is asynchronous (if supported by the DataSHIELD server)
        """
        self._init_errors()
        self.sessions()  # ensure sessions are started and available
        cmd = {}
        for conn in self.conns:
            name = resource
            if resources and conn.name in resources:
                name = resources[conn.name]
            if name:
                try:
                    res = conn.assign_resource(symbol, name, asynchronous)
                    cmd[conn.name] = res
                except Exception as e:
                    self._append_error(conn, e)
        self._do_wait(cmd)
        self._check_errors()

    def assign_expr(self, symbol: str, expr: str, asynchronous: bool = True) -> None:
        """
        Assign the result of the evaluation of an expression to a symbol in the DataSHIELD R session.

        :param symbol: The name of the destination symbol
        :param expr: The R expression to evaluate and which result will be assigned
        :param asynchronous: Whether the operation is asynchronous (if supported by the DataSHIELD server)
        """
        self._init_errors()
        self.sessions()  # ensure sessions are started and available
        cmd = {}
        for conn in self.conns:
            try:
                res = conn.assign_expr(symbol, expr, asynchronous)
                cmd[conn.name] = res
            except Exception as e:
                self._append_error(conn, e)
        self._do_wait(cmd)
        self._check_errors()

    def aggregate(self, expr: str, asynchronous: bool = True) -> dict:
        """
        Aggregate some data from the DataSHIELD R session using a valid R expression. The
        aggregation expression must satisfy the data repository's DataSHIELD configuration.

        :param expr: The R expression to evaluate and which result will be returned
        :param asynchronous: Whether the operation is asynchronous (if supported by the DataSHIELD server)
        :return: The result of the aggregation expression evaluation, per remote server name
        """
        self._init_errors()
        self.sessions()  # ensure sessions are started and available
        cmd = {}
        rval = {}
        for conn in self.conns:
            try:
                res = conn.aggregate(expr, asynchronous)
                cmd[conn.name] = res
            except Exception as e:
                self._append_error(conn, e)
                rval[conn.name] = None
        rval = self._do_wait(cmd)
        self._check_errors()
        return rval

    #
    # Private functions
    #

    def _do_wait(self, cmd: dict) -> dict:
        """
        Wait for asynchronous calls to complete and return results
        """
        rval = {}
        while cmd:
            for conn in self.conns:
                if conn.name in cmd:
                    res = cmd[conn.name]
                    # print(f"..checking {conn.name} -> {res.is_completed()}")
                    if res.is_completed():
                        try:
                            rval[conn.name] = res.fetch()
                        except Exception as e:
                            self._append_error(conn, e)
                        cmd.pop(conn.name, None)
                else:
                    conn.keep_alive()
            time.sleep(0.1)
        return rval

    def _init_errors(self) -> None:
        """
        Prepare for storing errors.
        """
        self.errors = {}

    def _append_error(self, conn: DSConnection, error: Exception) -> None:
        """
        Append an error.
        """
        self.errors[conn.name] = error

    def _check_errors(self) -> None:
        """
        Prepare for storing errors.
        """
        if self.errors:
            raise DSError("There are some errors, please check them with DSSession.get_errors().")
