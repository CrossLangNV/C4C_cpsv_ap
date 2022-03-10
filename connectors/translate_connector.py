from pathlib import Path
from urllib.parse import urljoin

import requests


class ETranslationConnector:
    base_url = 'https://etranslation.cefat4cities.crosslang.com'
    url_info = urljoin(base_url + '/', 'info')
    url_trans_snippet = urljoin(base_url + '/', 'translate/snippet')
    url_trans_snippet_id = urljoin(url_trans_snippet + '/', '{id}')
    url_trans_snippet_blocking = urljoin(url_trans_snippet + '/', 'blocking')
    url_trans_doc = urljoin(base_url + '/', 'translate/document')
    url_trans_doc_id = urljoin(url_trans_doc + '/', '{id}')
    url_trans_doc_blocking = urljoin(url_trans_doc + '/', 'blocking')

    def __init__(self, username: str, password: str):
        self._username = username
        self._password = password

    def info(self):
        r = requests.get(url=self.url_info, auth=(self._username, self._password))
        return r.json()

    def trans_snippet(self,
                      source: str,
                      target: str,
                      snippet: str):
        """
        Args:
            source:
            target:
            snippet:
        Returns:
            the request id
        """
        data = {'source': str(source),
                'target': str(target),
                'snippet': str(snippet)}

        r = requests.post(self.url_trans_snippet, data=data, auth=(self._username, self._password))

        return r.json()

    def trans_snippet_id(self, request_id):
        r = requests.get(self.url_trans_snippet_id.format(id=request_id), auth=(self._username, self._password))

        return r.json().get('content')

    def trans_snippet_blocking(self, source: str,
                               target: str,
                               snippet: str):
        data = {'source': str(source),
                'target': str(target),
                'snippet': str(snippet)}

        r = requests.post(self.url_trans_snippet_blocking, data=data, auth=(self._username, self._password))

        return r.json()

    def trans_doc(self, source: str,
                  target: str,
                  filename: Path):
        with open(filename, 'rb') as f:
            data = {'source': str(source),
                    'target': str(target),
                    # 'file': f
                    }

            files = {'file': f}

            r = requests.post(self.url_trans_doc,
                              data=data,
                              files=files, auth=(self._username, self._password))
        if r:
            return r.json()
        else:
            return None

    def trans_doc_id(self, request_id):
        """
        Args:
            request_id:
        Returns:
            raw bytestring
        """

        with requests.get(self.url_trans_doc_id.format(id=request_id), auth=(self._username, self._password)) as r:
            # Magic filename

            if r.status_code > 200:
                return None

            print(r.headers.get('Content-Disposition'))
            filename = r.headers.get('Content-Disposition').split('filename=')[1]

            return {'content': r.content,
                    'filename': filename}

    def trans_doc_blocking(self, source: str,
                           target: str,
                           filename: Path):
        with open(filename, 'rb') as f:
            data = {'source': str(source),
                    'target': str(target),
                    }

            files = {'file': f}

            r = requests.post(self.url_trans_doc_blocking,
                              data=data,
                              files=files, auth=(self._username, self._password))

            if r.status_code > 300:
                raise Exception(f'{r}\n{r.text}')

            # Magic filename
            filename_trans = r.headers.get('Content-Disposition').split('filename=')[1]

            return {'content': r.content,
                    'filename': filename_trans}
