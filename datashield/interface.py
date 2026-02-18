"""
Classes to be implemented for each data repository type.
"""

import importlib
import logging
import os
import yaml
from pydantic import BaseModel, Field

# Default configuration file paths to look for DataSHIELD login information, in order of precedence
CONFIG_FILES = ["~/.config/datashield/config.yaml", "./.datashield/config.yaml"]


class DSLoginInfo(BaseModel):
    """
    Helper class with DataSHIELD login details.
    """

    name: str
    url: str
    user: str | None = None
    password: str | None = None
    token: str | None = None
    profile: str = "default"
    driver: str = "datashield_opal.OpalDriver"

    model_config = {"extra": "forbid"}


class DSConfig(BaseModel):
    """
    Helper class with DataSHIELD configuration details.
    """

    servers: list[DSLoginInfo] = Field(default_factory=list)

    model_config = {"extra": "forbid"}

    @classmethod
    def load(cls) -> "DSConfig":
        """
        Load the DataSHIELD configuration from default configuration files. The file must contain
        a list of servers with their login details. The configuration from the first file found will be loaded,
        in order of precedence. If multiple files are found, the configurations will be merged, with new server
        details replacing existing ones by name.

        :return: The DataSHIELD configuration object
        """
        merged_config = None
        for config_file in CONFIG_FILES:
            try:
                # check file exists and is readable, if not, silently ignore
                if not os.path.exists(config_file):
                    continue
                if not os.access(config_file, os.R_OK):
                    continue
                config = cls.load_from_file(config_file)
                if merged_config is None:
                    merged_config = config
                else:
                    # merge servers by name, new ones replacing existing ones, and keep the rest of existing ones
                    existing_servers = {x.name: x for x in merged_config.servers}
                    for server in config.servers:
                        existing_servers[server.name] = server
                    merged_config.servers = list(existing_servers.values())
            except Exception as e:
                # silently ignore errors, e.g. file not found or invalid format
                logging.error(f"Failed to load login information from {config_file}: {e}")
        return merged_config if merged_config else cls()

    @classmethod
    def load_from_file(cls, file: str) -> "DSConfig":
        """
        Load the DataSHIELD configuration from a YAML file. The file must contain a list of servers with their login details.

        :param file: The path to the YAML file containing the DataSHIELD configuration
        :return: The DataSHIELD configuration object
        """
        with open(file) as f:
            config_data = yaml.safe_load(f)

        if config_data is None:
            config_data = {}

        return cls.model_validate(config_data)


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

        :return: Whether the result is completed
        """
        raise NotImplementedError("DSResult function not available")

    def fetch(self) -> any:
        """
        Wait for the result to be available and fetch the result from a previous assignment or aggregation operation that may have been
        run asynchronously, in which case it is a one-shot call. When the assignment or aggregation operation was not asynchronous,
        the result is wrapped in the object and can be fetched multiple times.

        :return: The result of the assignment or aggregation operation
        """
        raise NotImplementedError("DSResult function not available")


class RSession:
    """
    R Session (server side) class to a DataSHIELD server.
    """

    def is_started(self) -> bool:
        """
        Get whether the session has been started. This call must not wait for the session to
        be started, immediate response is expected.

        :return: Whether the session has been started
        """
        raise NotImplementedError("RSession function not available")

    def is_ready(self) -> bool:
        """
        Get whether the session is ready for receiving requests. This call must not
        wait for the session to be ready, immediate response is expected.

        :return: Whether the session is ready
        :throws: DSError if the session was not started or session information is not available
        """
        raise NotImplementedError("RSession function not available")

    def is_pending(self) -> bool:
        """
        Get whether the session is pending, i.e., it is in the process of being started but is
        not ready yet. This call must not wait for the session to be pending, immediate response
        is expected.

        :return: Whether the session is pending
        :throws: DSError if the session was not started or session information is not available
        """
        raise NotImplementedError("RSession function not available")

    def is_failed(self) -> bool:
        """
        Get whether the session has failed to start. This call must not
        wait for the session to have failed, immediate response is expected.

        :return: Whether the session has failed
        :throws: DSError if the session was not started or session information is not available
        """
        raise NotImplementedError("RSession function not available")

    def is_terminated(self) -> bool:
        """
        Get whether the session is terminated. This call must not wait for the session to be
        terminated, immediate response is expected.

        :return: Whether the session is terminated
        :throws: DSError if the session was not started or session information is not available
        """
        raise NotImplementedError("RSession function not available")

    def get_last_message(self) -> str:
        """
        Get a message describing the current state of the session, which can be used for debugging or logging purposes.

        :return: The session state message
        :throws: DSError if the session was not started or session information is not available
        """
        raise NotImplementedError("RSession function not available")


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

        :return: The list of available table names
        """
        raise NotImplementedError("DSConnection function not available")

    def has_table(self, name: str) -> bool:
        """
        Check whether a table with provided name exists in the data repository.

        :param name: The name of the table to check
        :return: Whether a table with provided name exists in the data repository
        """
        raise NotImplementedError("DSConnection function not available")

    def list_resources(self) -> list:
        """
        List available resource names from the data repository.

        :return: The list of available resource names
        """
        raise NotImplementedError("DSConnection function not available")

    def has_resource(self, name: str) -> bool:
        """
        Check whether a resource with provided name exists in the data repository.

        :param name: The name of the resource to check
        :return: Whether a resource with provided name exists in the data repository
        """
        raise NotImplementedError("DSConnection function not available")

    #
    # R Session (server side)
    #

    def has_session(self) -> bool:
        """
        Check whether a session is already established with the DataSHIELD server.

        :return: Whether a session is already established
        """
        raise NotImplementedError("DSConnection function not available")

    def start_session(self, asynchronous: bool = True) -> RSession:
        """
        Start an R session with the DataSHIELD server. If a session is already established, the existing session will be returned.

        :param asynchronous: Whether the session should be started asynchronously (if supported by the DataSHIELD server)
        :return: The R session object
        """
        raise NotImplementedError("DSConnection function not available")

    def is_session_started(self) -> bool:
        """
        Get whether the session with the DataSHIELD server is started. If the session start was asynchronous, this function
        can be used to check whether the session is started without waiting for it to be started. If the last call was positive,
        subsequent calls will not request the server for session status, but will return True directly. If the last call was negative,
        subsequent calls will request the server for session status until a positive response is obtained.

        :return: Whether the session is started
        :throws: DSError if the session was not started or session information is not available
        """
        raise NotImplementedError("DSConnection function not available")

    def get_session(self) -> RSession:
        """
        Get the R session with the DataSHIELD server. If no session is established, an error will be raised.

        :return: The R session object
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
        :param variables: The list of variable names to assign, or None to assign all variables
        :param missings: Whether to include missing values in the assignment (default: False)
        :param identifiers: Name of the identifiers mapping to use when assigning entities to R (if supported by the data repository).
        :param id_name: Name of the column that will contain the entity identifiers. If not specified, the identifiers will be the data
            frame row names. When specified this column can be used to perform joins between data frames.
        :param asynchronous: Whether the operation is asynchronous (if supported by the DataSHIELD server)
        :return: The result of the assignment operation
        """
        raise NotImplementedError("DSConnection function not available")

    def assign_resource(self, symbol: str, resource: str, asynchronous: bool = True) -> DSResult:
        """
        Assign a resource from the data repository to a symbol in the DataSHIELD R session.

        :param symbol: The name of the destination symbol
        :param resource: The name of the resource to assign
        :param asynchronous: Whether the operation is asynchronous (if supported by the DataSHIELD server)
        :return: The result of the assignment operation
        """
        raise NotImplementedError("DSConnection function not available")

    def assign_expr(self, symbol: str, expr: str, asynchronous: bool = True) -> DSResult:
        """
        Assign the result of the evaluation of an expression to a symbol in the DataSHIELD R session.

        :param symbol: The name of the destination symbol
        :param expr: The R expression to evaluate and which result will be assigned
        :param asynchronous: Whether the operation is asynchronous (if supported by the DataSHIELD server)
        :return: The result of the assignment operation
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
        :return: The result of the aggregation operation
        """
        raise NotImplementedError("DSConnection function not available")

    #
    # Symbols
    #

    def list_symbols(self) -> list:
        """
        After assignments have been performed, some symbols live in the DataSHIELD R session on the server side.
        :return: The list of symbols that live in the DataSHIELD R session on the server side
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
        :return: The list of available DataSHIELD profile names in the data repository
        """
        raise NotImplementedError("DSConnection function not available")

    def list_methods(self, type: str = "aggregate") -> list:
        """
        Get the list of DataSHIELD methods that have been configured on the remote data repository.

        :param type: The type of method, either "aggregate" (default) or "assign"
        :return: The list of DataSHIELD methods that have been configured on the remote data repository for the specified type
        """
        raise NotImplementedError("DSConnection function not available")

    def list_packages(self) -> list:
        """
        Get the list of DataSHIELD packages with their version, that have been configured on the remote data repository.

        :return: The list of DataSHIELD packages with their version, that have been configured on the remote data repository
        """
        raise NotImplementedError("DSConnection function not available")

    #
    # Workspaces
    #

    def list_workspaces(self) -> list:
        """
        Get the list of DataSHIELD workspaces, that have been saved on the remote data repository.

        :return: The list of DataSHIELD workspaces, that have been saved on the remote data repository
        """
        raise NotImplementedError("DSConnection function not available")

    def save_workspace(self, name: str) -> list:
        """
        Save the DataSHIELD R session in a workspace on the remote data repository.

        :param name: The name of the workspace
        :return: The list of DataSHIELD workspaces, that have been saved on the remote data repository after saving the workspace
        """
        raise NotImplementedError("DSConnection function not available")

    def restore_workspace(self, name: str) -> list:
        """
        Restore a saved DataSHIELD R session from the remote data repository. When restoring a workspace,
        any existing symbol or file with same name will be overridden.

        :param name: The name of the workspace
        :return: The list of DataSHIELD workspaces, that have been saved on the remote data repository after restoring the workspace
        """
        raise NotImplementedError("DSConnection function not available")

    def rm_workspace(self, name: str) -> list:
        """
        Remove a DataSHIELD workspace from the remote data repository. Ignored if no
        such workspace exists.

        :param name: The name of the workspace
        :return: The list of DataSHIELD workspaces, that have been saved on the remote data repository after removing the workspace
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
        resource assignment operation ('assign_resource'), expression assignment operation ('assign_expr')
        and R session creation ('session').

        :return: A named list of logicals specifying if asynchronicity is supported.
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
    def load_class(cls, name: str) -> type["DSDriver"]:
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
