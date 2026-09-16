import os
from configparser import ConfigParser


class ConfigHandler(object):
    """Read configuration from an INI file or a ``.env`` file.

    INI files use sections directly (``[db_server]`` -> ``{'host': ...}``).

    ``.env`` files have no sections, so the section name becomes an uppercase
    prefix separated from keys by a double underscore. For example, section
    ``db_server`` and key ``host`` map to ``DB_SERVER__HOST``. Returned keys are
    lowercased so they match what callers expect (``psycopg2.connect``, etc.).

    If a ``.env`` file is not found, the live OS environment is used instead
    (same prefix convention), allowing configuration without any file at all.
    """

    def __init__(self, config_file, config_file_section):
        self.config_file = config_file
        self.config_file_section = config_file_section

    def read_config(self):
        if str(self.config_file).endswith('.env'):
            return self._read_env_config()
        return self._read_ini_config()

    def _read_ini_config(self):
        parser = ConfigParser()
        parser.read(self.config_file)

        config = {}
        if parser.has_section(self.config_file_section):
            for key, value in parser.items(self.config_file_section):
                config[key] = value
        else:
            raise Exception(
                'Section {0} not found in file {1}'.format(
                    self.config_file_section, self.config_file
                )
            )

        return config

    def _read_env_config(self):
        prefix = self._env_prefix(self.config_file_section)

        if os.path.isfile(self.config_file):
            source = self._parse_dotenv(self.config_file)
        else:
            # Fall back to the live environment when no .env file is present.
            source = os.environ

        config = {}
        for key, value in source.items():
            upper_key = key.upper()
            if upper_key.startswith(prefix):
                config[upper_key[len(prefix):].lower()] = value

        if not config:
            raise Exception(
                'No {0}* variables found in {1} or the environment'.format(
                    prefix, self.config_file
                )
            )

        return config

    @staticmethod
    def _env_prefix(section):
        return section.upper().replace('-', '_').replace('.', '_') + '__'

    @staticmethod
    def _parse_dotenv(path):
        """Parse a simple ``KEY=VALUE`` .env file into a dict."""
        values = {}
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue

                key, _, value = line.partition('=')
                key = key.strip()
                if not key:
                    continue

                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                    value = value[1:-1]

                values[key] = value

        return values
