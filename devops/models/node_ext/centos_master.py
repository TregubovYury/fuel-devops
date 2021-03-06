
#    Copyright 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os

from devops.helpers.cloud_image_settings import generate_cloud_image_settings
from devops.helpers.helpers import wait_tcp
from devops import logger
from devops import settings


class NodeExtension(object):
    """Extension for Centos Master node"""

    def __init__(self, node):
        self.node = node

    def bootstrap_and_wait(self):
        self.node.start()
        ip = self.node.get_ip_address_by_network_name(
            settings.SSH_CREDENTIALS['admin_network'])
        wait_tcp(host=ip, port=self.node.ssh_port,
                 timeout=self.node.bootstrap_timeout,
                 timeout_msg='Failed to bootstrap centos master')
        logger.info('Centos cloud image bootstrap complete')

    def deploy_wait(self):
        # Do nothing
        logger.warning('Fuel is going to be installed manually in tests')

    def get_kernel_cmd(self, **kwargs):
        return None

    def post_define(self):
        """Builds setting iso to send basic configuration for cloud image"""

        cloud_image_settings_path = os.path.join(
            settings.CLOUD_IMAGE_DIR, 'cloud_settings.iso')
        admin_ip = self.node.get_ip_address_by_network_name(
            settings.SSH_CREDENTIALS['admin_network'])
        interface = self.node.get_interface_by_network_name(
            settings.SSH_CREDENTIALS['admin_network'])
        interface_name = interface.label
        user = settings.SSH_CREDENTIALS['login']
        password = settings.SSH_CREDENTIALS['password']
        admin_ap = interface.l2_network_device.address_pool
        gateway = str(admin_ap.gateway)
        admin_netmask = str(admin_ap.ip_network.netmask)
        admin_network = str(admin_ap.ip_network)
        dns = settings.DEFAULT_DNS
        dns_ext = dns
        hostname = settings.DEFAULT_MASTER_FQDN

        generate_cloud_image_settings(
            cloud_image_settings_path=cloud_image_settings_path,
            admin_network=admin_network,
            interface_name=interface_name,
            admin_ip=admin_ip,
            admin_netmask=admin_netmask,
            gateway=gateway,
            dns=dns,
            dns_ext=dns_ext,
            hostname=hostname,
            user=user,
            password=password
        )

        self.node.get_volume(name='iso').upload(cloud_image_settings_path)
