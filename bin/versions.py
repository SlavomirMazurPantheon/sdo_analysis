# Copyright The IETF Trust 2021, All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = "Slavomir Mazur"
__copyright__ = "Copyright The IETF Trust 2021, All Rights Reserved"
__license__ = "Apache License, Version 2.0"
__email__ = "slavomir.mazur@pantheon.tech"
__version__ = "1.1.0"

import configparser as ConfigParser
import json
from subprocess import CalledProcessError, check_output

import pyang
from xym import __version__ as xym_version


class ValidatorsVersions:
    def __init__(self):
        config_path = '/etc/yangcatalog/yangcatalog.conf'
        config = ConfigParser.ConfigParser()
        config._interpolation = ConfigParser.ExtendedInterpolation()
        config.read(config_path)
        confdc_exec = config.get('Tool-Section', 'confdc-exec')
        self.cache_dir = config.get('Directory-Section', 'cache')

        # ConfD version
        try:
            confd_version = check_output('{} --version'.format(confdc_exec), shell=True).decode('utf-8').rstrip()
        except CalledProcessError:
            confd_version = 'undefined'
        # yangdump version
        try:
            yangdump_cmd = '/usr/bin/yangdump-pro'
            yangdump_version = check_output('{} --version'.format(yangdump_cmd), shell=True).decode('utf-8').strip()
        except CalledProcessError:
            yangdump_version = 'undefined'
        # yanglint version
        yanglint_cmd = '/usr/local/bin/yanglint'
        yanglint_version = check_output('{} --version'.format(yanglint_cmd), shell=True).decode('utf-8').rstrip()

        self.versions = {'validator_version': __version__, 'pyang_version': pyang.__version__, 'xym_version': xym_version,
                         'confd_version': confd_version, 'yanglint_version': yanglint_version,
                         'yangdump_version': yangdump_version}

    def get_versions(self):
        return self.versions
