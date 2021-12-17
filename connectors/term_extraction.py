import warnings

import requests


class ConnectorTermExtraction:
    """
    Connects to the Term Extraction API
    """

    def __init__(self, url,
                 test_connection: bool = True):
        """

        Args:
            url:
                URL of the API
            test_connection:
                flag to make a small connection check. Disable for slightly faster init.
        """

        self.url = url

        if test_connection:
            try:
                requests.get(url)
            except requests.exceptions.ConnectionError as e:
                warnings.warn(f"Can't reach API.\n{e}", ConnectionWarning)


class ConnectionWarning(Warning):
    """
    Custom warning when the connection might be lost.
    """
