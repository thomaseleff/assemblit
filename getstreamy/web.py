"""
Information
---------------------------------------------------------------------
Name        : web.py
Location    : ~/
Author      : Tom Eleff
Published   : 2024-XX-XX
Revised on  : .

Description
---------------------------------------------------------------------
Web request handler class for retrieving information from a Github
web-page.
"""

import requests
import urllib.parse as up
from bs4 import BeautifulSoup


class Handler():

    def __init__(
        self,
        url: str
    ):
        """ Initializes an instance of the web-handler Class().

        Parameters
        ----------
        url : `str`
            Web-address of a GitHub repository
        """

        self.url = url

    def get_readme(
        self,
        name: str = ''
    ) -> str:
        """ Initializes an instance of the home-page Class().

        Parameters
        ----------
        name : `str`
            Name of the markdown document to display as the web-page content
        """

        if name:

            request = requests.get(
                url=up.urljoin(
                    self.url,
                    'main/%s' % (name)
                )
            )

        else:

            request = requests.get(
                url=self.url
            )

        if request.status_code == 200:

            # Parse the html text content
            content = BeautifulSoup(request.text, 'lxml')

            return content

        else:

            return None
