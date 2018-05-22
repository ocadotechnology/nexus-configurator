import json
import os.path
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def requests_retry(
    retries=10,
    backoff_factor=0.3,
    status_forcelist=(429, 500, 502, 503, 504),
    session=None,
):
    """Retry a request upto `retries` with exponential backoff_factor

    see: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    """
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


class NexusUnauthorised(Exception):
    pass


class NexusConnectionError(Exception):
    pass


class Nexus(object):
    """A Nexus client

    Will attempt to connect to the Nexus instance ping endpoint using
    the provided credentials.

    A connection error or timeout will retry with a backoff

    :param host: the base url of the nexus instance
    :param user: the admin username
    :param password: the password for the admin username
    """
    def __init__(self, host, user, password):
        super(Nexus, self).__init__()
        self.host = host
        self.api_prefix = "service/rest/v1"
        s = requests.Session()
        s.auth = (user, password)
        self.requests = requests_retry(session=s)
        ping_url = "{}/service/metrics/ping".format(self.host)
        try:
            resp = self.requests.get(ping_url, timeout=3)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as herr:
            if herr.response.status_code == 401:
                raise NexusUnauthorised(herr)
        except requests.exceptions.ConnectionError:
            raise NexusConnectionError

    def _post(self, endpoint, payload, content_type='application/json'):
        url = "{}/{}/{}".format(self.host, self.api_prefix, endpoint)
        headers = {'Content-type': content_type}
        data = json.dumps(payload)
        return self.requests.post(url, data=data, headers=headers, timeout=3)

    def _put(self, endpoint, payload, content_type='application/json'):
        url = "{}/{}/{}".format(self.host, self.api_prefix, endpoint)
        headers = {'Content-type': content_type}
        data = json.dumps(payload)
        return self.requests.put(url, data=data, headers=headers, timeout=3)

    def _get(self, endpoint):
        url = "{}/{}/{}".format(self.host, self.api_prefix,
                                endpoint, timeout=3)
        return self.requests.get(url)

    def _delete(self, endpoint):
        url = "{}/{}/{}".format(self.host, self.api_prefix,
                                endpoint, timeout=3)
        return self.requests.delete(url)

    def delete_script(self, name):
        return self._delete("script/{}".format(name))

    def delete_all_scripts(self):
        scripts_names = [d["name"] for d in self.scripts]
        for script_name in scripts_names:
            self.delete_script(script_name)

    def create_script(self, filename, name=None):
        with open(filename, 'r') as f:
            script = f.read()
        script = script.replace("\n", '\n')
        script = script.replace("\"", '\"')
        if not name:
            basename = os.path.basename(filename)
            name = os.path.splitext(basename)[0]
        payload = {"name": name, "type": "groovy", "content": script}
        resp = self._put("script/{}".format(name), payload)
        if resp.status_code == 404:
            resp = self._post("script", payload)
        return resp

    def run_script(self, script, **kwargs):
        run_url = "script/{}/run".format(script)
        return self._post(run_url, kwargs, content_type="text/plain")

    @property
    def scripts(self):
        resp = self._get("script/").text
        return resp.json()
