"""
DataSHIELD utils.
"""

class DSLoginBuilder:
    """
    Helper class to formalize DataSHIELD login arguments for a set of servers.
    """

    def __init__(self):
        self.items = list()
    
    def add(self, name: str, url: str, user: str = None, password: str = None, token: str = None, profile: str = 'default'):
        self.items.append({
            'name': name,
            'url': url,
            'user': user,
            'password': password,
            'token': token,
            'profile': profile
        })
        return self
    
    def build(self):
        return self.items