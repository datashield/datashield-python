"""
Classes to be implemented for each data repository type.
"""

import importlib


class DSLoginInfo:
    """
    Helper class with DataSHIELD login details.
    """

    def __init__(
        self,
        name: str,
        url: str,
        user: str = None,
        password: str = None,
        token: str = None,
        profile: str = "default",
        driver: str = "datashield_opal.OpalDriver",
    ):
        self.items = []
        self.name = name
        self.url = url
        self.user = user
        self.password = password
        self.token = token
        self.profile = profile if profile is not None else "default"
        self.driver = driver if driver is not None else "datashield_opal.OpalDriver"


class DSResult:
    """
    This virtual class describes the result and state of execution of
    a DataSHIELD request (aggregation or assignment).
    """

    def is_completed(self) -> bool:
        """
        Get whether the result from a previous assignment or aggregation operation was
        completed, either with a successful status or a failed one. This call must not
        wait for the completion, immediate response is expected. Once the result is
        identified as being completed, the raw result the operation can be get directly.
        """
        raise NotImplementedError("DSResult function not available")

    def fetch(self) -> any:
        """
        Wait for the result to be available and fetch the result from a previous assignment or aggregation operation that may have been
        run asynchronously, in which case it is a one-shot call. When the assignment or aggregation operation was not asynchronous,
        the result is wrapped in the object and can be fetched multiple times.
        """
        raise NotImplementedError("DSResult function not available")


class DSConnection:
    """
    Connection class to a DataSHIELD server.
    """

    #
    # Content listing
    #

    def list_tables(self) -> list:
        """
        List available table names from the data repository.
        """
        raise NotImplementedError("DSConnection function not available")

    def has_table(self, name: str) -> bool:
        """
        Check whether a table with provided name exists in the data repository.

        Parameters
        ----------
        :param name: The name of the table to check
        """
        raise NotImplementedError("DSConnection function not available")

    def list_resources(self) -> list:
        """
        List available resource names from the data repository.
        """
        raise NotImplementedError("DSConnection function not available")

    def has_resource(self, name: str) -> bool:
        """
        Check whether a resource with provided name exists in the data repository.

        :param name: The name of the resource to check
        """
        raise NotImplementedError("DSConnection function not available")

    #
    # Assign
    #

    def assign_table(
        self,
        symbol: str,
        table: str,
        variables: list = None,
        missings: bool = False,
        identifiers: str = None,
        id_name: str = None,
        asynchronous: bool = True,
    ) -> DSResult:
        """
        Assign a data table from the data repository to a symbol in the DataSHIELD R session.

        :param symbol: The name of the destination symbol
        :param table: The name of the table to assign
        :param asynchronous: Whether the operation is asynchronous (if supported by the DataSHIELD server)
        """
        raise NotImplementedError("DSConnection function not available")

    def assign_resource(self, symbol: str, resource: str, asynchronous: bool = True) -> DSResult:
        """
        Assign a resource from the data repository to a symbol in the DataSHIELD R session.

        :param symbol: The name of the destination symbol
        :param resource: The name of the resource to assign
        :param asynchronous: Whether the operation is asynchronous (if supported by the DataSHIELD server)
        """
        raise NotImplementedError("DSConnection function not available")

    def assign_expr(self, symbol: str, expr: str, asynchronous: bool = True) -> DSResult:
        """
        Assign the result of the evaluation of an expression to a symbol in the DataSHIELD R session.

        :param symbol: The name of the destination symbol
        :param expr: The R expression to evaluate and which result will be assigned
        :param asynchronous: Whether the operation is asynchronous (if supported by the DataSHIELD server)
        """
        raise NotImplementedError("DSConnection function not available")

    #
    # Aggregate
    #

    def aggregate(self, expr: str, asynchronous: bool = True) -> DSResult:
        """
        Aggregate some data from the DataSHIELD R session using a valid R expression. The
        aggregation expression must satisfy the data repository's DataSHIELD configuration.

        :param expr: The R expression to evaluate and which result will be returned
        :param asynchronous: Whether the operation is asynchronous (if supported by the DataSHIELD server)
        """
        raise NotImplementedError("DSConnection function not available")

    #
    # Symbols
    #

    def list_symbols(self) -> list:
        """
        After assignments have been performed, some symbols live in the DataSHIELD R session on the server side.
        """
        raise NotImplementedError("DSConnection function not available")

    def rm_symbol(self, name: str) -> None:
        """
        After symbol removal, the data identified by the symbol will not be accessible in the DataSHIELD R session on the server side.

        :param name: The name of symbol to remove
        """
        raise NotImplementedError("DSConnection function not available")

    #
    # DataSHIELD config
    #

    def list_profiles(self) -> list:
        """
        List available DataSHIELD profile names in the data repository.
        """
        raise NotImplementedError("DSConnection function not available")

    def list_methods(self, type: str = "aggregate") -> list:
        """
        Get the list of DataSHIELD methods that have been configured on the remote data repository.

        :param type: The type of method, either "aggregate" (default) or "assign"
        """
        raise NotImplementedError("DSConnection function not available")

    def list_packages(self) -> list:
        """
        Get the list of DataSHIELD packages with their version, that have been configured on the remote data repository.
        """
        raise NotImplementedError("DSConnection function not available")

    #
    # Workspaces
    #

    def list_workspaces(self) -> list:
        """
        Get the list of DataSHIELD workspaces, that have been saved on the remote data repository.
        """
        raise NotImplementedError("DSConnection function not available")

    def save_workspace(self, name: str) -> list:
        """
        Save the DataSHIELD R session in a workspace on the remote data repository.

        :param name: The name of the workspace
        """
        raise NotImplementedError("DSConnection function not available")

    def restore_workspace(self, name: str) -> list:
        """
        Restore a saved DataSHIELD R session from the remote data repository. When restoring a workspace,
        any existing symbol or file with same name will be overridden.

        :param name: The name of the workspace
        """
        raise NotImplementedError("DSConnection function not available")

    def rm_workspace(self, name: str) -> list:
        """
        Remove a DataSHIELD workspace from the remote data repository. Ignored if no
        such workspace exists.

        :param name: The name of the workspace
        """
        raise NotImplementedError("DSConnection function not available")

    #
    # Utils
    #

    def is_async(self) -> dict:
        """
        When a DSResult object is returned on aggregation or assignment operation,
        the raw result can be accessed asynchronously, allowing parallelization of DataSHIELD calls
        over multpile servers. The returned named list of logicals will specify if asynchronicity is supported for:
        aggregation operation ('aggregate'), table assignment operation ('assign_table'),
        resource assignment operation ('assign_resource') and expression assignment operation ('assign_expr').
        """
        raise NotImplementedError("DSConnection function not available")

    def keep_alive(self) -> None:
        """
        As the DataSHIELD sessions are working in parallel, this function helps at keeping
        idle connections alive while others are working. Any communication failure must
        be silently processed.
        """
        raise NotImplementedError("DSConnection function not available")

    def disconnect(self) -> None:
        """
        This closes the connection, discards all pending work, and frees resources (e.g., memory, sockets).
        """
        raise NotImplementedError("DSConnection function not available")


class DSDriver:
    """
    Driver class for instanciating a connection object by driver name.
    """

    @classmethod
    def new_connection(cls, args: DSLoginInfo, restore: str = None) -> DSConnection:
        """
        Creates a new connection

        :param args: The connection arguments, as a DSLoginInfo object
        :param restore: The workspace name to be restored
        """
        raise NotImplementedError("DSConnection function not available")

    @classmethod
    def load_class(cls, name: str) -> any:
        """
        Load a class from its fully qualified name (dot separated).

        :param name: The driver class name
        :return: The class of the driver on which the ``new_connection()`` function will be called
        """
        names = name.split(".")
        className = names.pop()
        moduleName = ".".join(names)
        return getattr(importlib.import_module(moduleName), className)


class DSError(Exception):
    """
    DataSHIELD error report.
    """

    def __init__(self, message: str = None):
        super().__init__(message)
        self.message = message

    def get_error(self) -> dict:
        """Get the error details as a named list with keys 'message', 'code' and 'details'."""
        pass

    def is_client_error(self) -> bool:
        """Get whether the error is a client error (e.g., invalid request, authentication failure, etc.)."""
        pass

    def is_server_error(self) -> bool:
        """Get whether the error is a server error (e.g., internal error, service unavailable, etc.)."""
        pass
