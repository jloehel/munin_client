"""Munin client module
"""

import re
import logging
from functools import wraps
import pexpect

GRAPH_CONFIG_PATTERN = re.compile(
    r"graph_(?P<name>\w+) (?P<value>.*)"
)
FIELD_CONFIG_PATTERN = re.compile(
    r"(?P<field>\w+)\.(?P<name>\w+) (?P<value>.*)"
)


def munin_function(func):
    """The munin_function decorator
    """
    @wraps(func)
    def deco(self, *args, **kwargs):
        if not self._connect():
            return "{}"
        result = func(self, *args, **kwargs)
        self._disconnect()
        return result
    return deco


class MuninClient(object):
    """Easy interaction with munin via python.

    Args:
        host (str): The hostname of the Munin node.
        port (int): The port of the Munin instance. The standard port is 4949.

    Attributes:
        _host (str): The hostname of the Munin instance.
        _port (int): The port of the Munin instance.
        _cli (spawn): The pexpect spwan object.
    """

    def __init__(self, host, port=4949):
        self._host = host
        self._port = port
        self._cli = None
        self.logger = logging.getLogger(__name__)

    def _connect(self):
        try:
            cmd = "nc {} {}".format(self._host, self._port)
            self._cli = pexpect.spawn(cmd)
            self._cli.expect("# munin node at .*")
            self.logger.debug("Connection successfully established.")
            return True
        except pexpect.ExceptionPexpect:
            self.logger.error("Can not connect to %s.", self._host)
            return False

    def _disconnect(self):
        if self._cli:
            self._cli.close()
            self.logger.debug("Connection successfully closed.")

    @munin_function
    def config(self, plugin_name):
        """This method implements the munin function "config".

        Args:
            plugin_name: The name of the munin plugin.

        Returns:
            A dictionary including the configuration for the specified
            plugin.
        """
        config = {
            "graph": {},
            "fields": {},
        }
        cmd = "config {}".format(plugin_name)
        self._cli.sendline(cmd)
        failure = r"config {}\r\n# Bad exit\r\n\.\r\n".format(plugin_name)
        success = r"config {}\r\n(.*)\r\n\.\r\n".format(plugin_name)
        response = self._cli.expect([failure, success])
        if response == 0:
            self.logger.error("Could not load the configuration for the plugin: %s", plugin_name)
            return {}
        elif response == 1:
            for line in self._cli.match.group(1).decode("utf-8").split("\r\n"):
                if GRAPH_CONFIG_PATTERN.search(line):
                    match = GRAPH_CONFIG_PATTERN.search(line)
                    config["graph"][match.group("name")] = match.group("value")
                if FIELD_CONFIG_PATTERN.search(line):
                    match = FIELD_CONFIG_PATTERN.search(line)
                    if match.group("field") not in config["fields"].keys():
                        config["fields"][match.group("field")] = {}
                    config["fields"][match.group("field")][
                        match.group("name")
                    ] = match.group("value")
            return config

    @munin_function
    def fetch(self, plugin_name):
        """This method implements the munin function "fetch".

        Args:
            plugin_name: The name of the munin plugin.

        Returns:
            A set including the values of the specified plugin.
        """
        cmd = "fetch {}".format(plugin_name)
        self._cli.sendline(cmd)
        failure = r"config {}\r\n# Bad exit\r\n\.\r\n".format(plugin_name)
        success = r"fetch {}\r\n(.*)\r\n.\r\n".format(plugin_name)
        response = self._cli.expect([failure, success])
        if response == 0:
            self.logger.error("Could not load the configuration for the plugin: %s", plugin_name)
            return {}
        if response == 1:
            raw_values = self._cli.match.group(1).decode("utf-8")
            return {v.split(" ")[0].split(".")[0]: v.split(" ")[1] for v
                    in raw_values.split("\r\n")}

    @munin_function
    def list(self):
        """This method implements the munin function "list".

        Returns:
            A list of all available plugins on this munin node.
        """
        self._cli.sendline("list")
        self._cli.expect(r"list\r\n(.*)\r\n")
        plugins = self._cli.match.group(1).decode("utf-8")
        return plugins.split(" ")

    @munin_function
    def nodes(self):
        """This method implements the munin function "nodes".

        Returns:
            The name of the munin node.
        """
        self._cli.sendline("nodes")
        self._cli.expect(r"nodes\r\n(.*)\r\n.\r\n")
        nodes = self._cli.match.group(1).decode("utf-8")
        return nodes

    @munin_function
    def version(self):
        """This method implements the munin function "version".

        Returns:
            The version of munin.
        """
        self._cli.sendline("version")
        self._cli.expect(r"munins node on .* version: (\d+.\d+.\d+)")
        version = self._cli.match.group(1).decode("utf-8")
        return version
