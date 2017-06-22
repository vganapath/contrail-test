import os,argparse,ConfigParser,sys,re
from common.connections import ContrailConnections
from common.contrail_test_init import ContrailTestInit
from fabric.api import run
from tools.configure import *
from keystone_tests import KeystoneCommands


class ContrailCluster():

    def __init__(self, issu_upgrade, new_version, new_image,
        fab_path='/opt/contrail/utils', test_directory='.', v1_testbed_py = None, v2_testbed_py=None,
        yml_b4_upgrade=None, yml_a4_upgrade=None):
        self.issu_upgrade = issu_upgrade
        self.new_version = new_version
        self.new_image = new_image
        self.v1_testbed_py = v1_testbed_py
        self.v2_testbed_py = v2_testbed_py
        self.fab_path = fab_path
        if 'PARAMS_FILE' in os.environ:
            self.ini_file = os.environ.get('PARAMS_FILE')
        else:
            configure_test_env(fab_path, test_directory)
            if os.path.isfile('sanity_params.ini'):
                self.ini_file = 'sanity_params.ini'
            else:
                raise self.skipTest('failed to find sanity_params.ini')
        self.inputs = ContrailTestInit(self.ini_file)
        self.connections = ContrailConnections(self.inputs)
        self.agent_inspect = self.connections.agent_inspect
        self.quantum_h = self.connections.quantum_h
        self.nova_h = self.connections.nova_h
        self.vnc_lib = self.connections.vnc_lib
        self.logger = self.inputs.logger
        self.analytics_obj = self.connections.analytics_obj

    def upgrade(self):
        if self.issu_upgrade == 'upgrade':
            #perform upgrade
            self.logger.info("STARTING UPGRADE")
            username = self.inputs.host_data[self.inputs.cfgm_ips[0]]['username']
            password = self.inputs.host_data[self.inputs.cfgm_ips[0]]['password']
            with settings(
                host_string='%s@%s' % (
                    username, self.inputs.cfgm_ips[0]),
                    warn_only=True, abort_on_prompts=False, debug=True):
                #status = run("cd /tmp/temp/;ls")
                status = run("ls "+self.new_image)
                self.logger.debug("%s" % status)
                status = run("cd " + self.fab_path)
                import pdb;pdb.set_trace()
                status = run("cd ~/fabric-utils;fab upgrade_contrail:"+self.new_version+","+self.new_image)
                assert not(
                    status.return_code), 'Failed in running'
        return True

    def ISSU(self):
        if self.issu_upgrade == 'issu':
            #perform issu
            pass

    def create_objects(self, yaml):
        #function to create objects based on the YAML file
        pass
   
    def verify_objects(self, yaml):
        #function to verify objects based on the YAML file    
        pass
    
  
    def get_current_version(self):
        #function to get the current version
        username = self.inputs.host_data[self.inputs.cfgm_ips[0]]['username']
        password = self.inputs.host_data[self.inputs.cfgm_ips[0]]['password']
        with settings(host_string='%s@%s' % (
                    username, self.inputs.cfgm_ips[0]),
                    warn_only=True, abort_on_prompts=False, debug=True):
            status = run("contrail-version | grep contrail-control | awk '{print $2}' | sed 's/-.*//g'")
        return status

    def verify_version(self, version):
       #function to verify the version
        username = self.inputs.host_data[self.inputs.cfgm_ips[0]]['username']
        password = self.inputs.host_data[self.inputs.cfgm_ips[0]]['password']
        with settings(host_string='%s@%s' % (
                    username, self.inputs.cfgm_ips[0]),
                    warn_only=True, abort_on_prompts=False, debug=True):
            import pdb;pdb.set_trace()
            status = run("contrail-version | grep contrail-control | awk '{print $2}' | sed 's/-.*//g'")
        if status == version:
            return True
        else:
            return False

    def update_keystone_endpoint(keystone, new_endpoint):
        uuid = keystone.__dict__['id']
        service_id = keystone.__dict__['service_id']
        publicurl = keystone.__dict__['publicurl']
        adminurl = keystone.__dict__['adminurl']
        region = keystone.__dict__['region']
        internalurl = keystone.__dict__['internalurl']
        keystone.__dict__['manager'].delete(uuid)
        keystone.__dict__['manager'].create(region=region, service_id=service_id,
            publicurl=publicurl, adminurl=adminurl, internalurl=internalurl)

    def get_neutron_endpoint(self):
        conn=self.connections
        keystone = KeystoneCommands(conn.username, conn.password, conn.project_name,
            conn.auth.auth_url, region_name=conn.auth.region_name)
        service_list = keystone.services_list()
        service_id = [service.__dict__['id'] for service in service_list if service.__dict__['name'] == 'neutron']
        endpoint = keystone.endpoints_list(service_id[0])
        return endpoint


def main(argv=sys.argv):
    ap = argparse.ArgumentParser(
        description='Configure test environment')
    ap.add_argument('contrail_test_directory', type=str, default='.',
                    help='contrail test directory')
    ap.add_argument('-p','--contrail-fab-path', type=str, default='/opt/contrail/utils',
                    help='Contrail fab path on local machine')
    args = ap.parse_args()

    cluster=ContrailCluster('upgrade', '4.1.0.0', '/root/contrail-fabric-utils-4.1.0.0-3076~mitaka.tgz',
        args.contrail_fab_path, args.contrail_test_directory)
    import pdb;pdb.set_trace()
    cluster.get_neutron_endpoint()
    #testbed_format_conversion(args.contrail_fab_path)
    #configure_test_env(args.contrail_fab_path, args.contrail_test_directory)

if __name__ == "__main__":
    sys.exit(not main(sys.argv))
