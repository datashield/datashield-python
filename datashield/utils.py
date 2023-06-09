"""
DataSHIELD utils.
"""

class DSLoginBuilder:
    """
    Helper class to formalize DataSHIELD login arguments for a set of servers.
    """

    def __init__(self):
        self.items = list()
    
    def add(self, name: str, url: str, user: str = None, password: str = None, token: str = None, profile: str = 'default', driver: str = 'datashield_opal.OpalDriver'):
        """
        Add DataSHIELD login information.

        :param name: The name of the server, must be unique
        :param url: The URL of the server
        :param user: The user name (required if token is None)
        :param password: The user password
        :param token: The access token (required if user is None)
        :param profile: The DataSHIELD profile name to be used
        :param driver: The DataSHIELD connection driver class full name 
        """
        if name is None:
            raise ValueError('Server name is missing')
        if url is None:
            raise ValueError('Server URL is missing')
        found = [x for x in self.items if x['name'] == name]
        if len(found) > 0:
            raise ValueError('Server name must be unique: %s' % name)
        if user is None and token is None:
            raise ValueError('Either user or token must be provided')
        self.items.append({
            'name': name,
            'url': url,
            'user': user,
            'password': password,
            'token': token,
            'profile': profile if profile is not None else 'default',
            'driver': driver if driver is not None else 'datashield_opal.OpalDriver'
        })
        return self
    
    def remove(self, name: str):
        """
        Remove the DataSHIELD login information by its name, if it exists.
        """
        self.items = [x for x in self.items if x['name'] != name]
        return self
    
    def build(self):
        return self.items
