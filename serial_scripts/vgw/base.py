import test_v1
from common.connections import ContrailConnections
from common import isolated_creds
from project_test import *
from vn_test import *
from vm_test import *


class BaseVgwTest(test_v1.BaseTestCase_v1):

    @classmethod
    def setUpClass(cls):
        super(BaseVgwTest, cls).setUpClass()
        cls.quantum_h = cls.connections.quantum_h
        cls.nova_h = cls.connections.nova_h
        cls.vnc_lib = cls.connections.vnc_lib
        cls.agent_inspect = cls.connections.agent_inspect
        cls.cn_inspect = cls.connections.cn_inspect
        cls.analytics_obj = cls.connections.analytics_obj
        cls.setup_common_objects()
    # end setUpClass

    @classmethod
    def tearDownClass(cls):
        for vn in cls.vn_fixture_dict:
            vn.verify_is_run = False
            vn.cleanUp()
        super(BaseVgwTest, cls).tearDownClass()
    # end tearDownClass

    @classmethod
    def setup_common_objects(cls):

        cls.project_fixture = ProjectFixture(
            project_name=cls.inputs.project_name,
            connections=cls.connections)
        cls.project_fixture.setUp()
        cls.logger.info(
            'Default SG to be edited for allow all on project: %s' %
            cls.inputs.project_name)
        cls.project_fixture.set_sec_group_for_allow_all(
            cls.inputs.project_name, 'default')

        # Formin the VGW VN dict for further test use
        cls.vgw_vn_list = {}
        cls.vn_fixture_dict = []
        if cls.inputs.vgw_data != []:
            for key in cls.inputs.vgw_data[0]:
                for vgw in cls.inputs.vgw_data[0][key]:
                    cls.vgw_vn_list[cls.inputs.vgw_data[0][key][vgw]['vn']] = {}
                    cls.vgw_vn_list[cls.inputs.vgw_data[0][key][vgw]['vn']][
                        'subnet'] = cls.inputs.vgw_data[0][key][vgw]['ipam-subnets']
                    cls.vgw_vn_list[cls.inputs.vgw_data[0]
                                    [key][vgw]['vn']]['host'] = key
                    if 'gateway-routes' in cls.inputs.vgw_data[0][key][vgw]:
                        cls.vgw_vn_list[cls.inputs.vgw_data[0][key][vgw]['vn']][
                            'route'] = cls.inputs.vgw_data[0][key][vgw]['gateway-routes']

            # Creating VN
            cls.vn_fixture_dict = []
            for key in cls.vgw_vn_list:
                vn = VNFixture(
                    project_name=key.split(':')[1],
                    option='contrail',
                    connections=cls.connections,
                    inputs=cls.inputs,
                    vn_name=key.split(":")[3],
                    subnets=cls.vgw_vn_list[key]['subnet'])
                cls.vn_fixture_dict.append(vn)
                vn.setUp()

    # end setup_common_objects
