#!/usr/bin/env python
import docker
import os
import unittest
from utils import DockerUtil

"""
SCENARIO - downloading Connect extensions in to extensions folder
    Verify extensions download over HTTP
"""
class DockerTestsExtensionsHTTP(unittest.TestCase):
    docker_image = ""
    container = ""
    test_yml = os.path.join('.','tmp','extensions-http.yml')
    composeCmd = 'docker-compose -f '+ test_yml +' -p mctest_extensions_http'
    max_wait_time = 120

    @classmethod
    def setUpClass(cls):
        print(' \n >>>> ==== Running Test extensions - Verify extensions download HTTP' + ' ===== ') 
        print( ' >>>> ==== using IMAGE = ' + cls.docker_image + ' ===== ')
        DockerUtil.empty_test_folder("tmp")

        # Setup test dir as volume to by mounted by container
        if os.name == 'nt':
            DockerUtil.create_test_dir("tmp")
            os.system('xcopy /E /I /Y .\\testdata\\web .\\tmp\\web')
        else:
            DockerUtil.create_test_dir("tmp")
            os.system('cp -r ./testdata/web ./tmp/web')
        DockerUtil.generate_compose_yml(cls.test_yml, cls.docker_image, 'extensions-http.yml')
        
        # Run docker compose
        os.system(cls.composeCmd + " up -d")
        client = docker.from_env()
        cls.container = client.containers.get("mctest_extensions_http-mc-1")

    def test_extensions_http(self):
        # HTTP download

        # expect to find downloading extensions in to folder
        # expect to see Connect start
        try:
            # wait for extensions download message
            DockerUtil.wait_for_log_message([self.container], "Downloading extensions at", self.max_wait_time)
            DockerUtil.wait_for_log_message([self.container], "Unzipping contents of", self.max_wait_time)
            
	        # Verify plugin.xml file for each test Extensions in MC extensions folder
	        # retrieve container extensions folder 
            exts = DockerUtil.list_container_dir(self.__class__.container,"/opt/connect/extensions/")
            self.assertTrue(("extensions/testExtension3/plugin.xml" in exts) and ("extensions/testExtension2/plugin.xml" in exts) and ("extensions/testExtension1/plugin.xml" in exts))
        
            # wait for MC to come up
            DockerUtil.wait_for_containers([self.container], self.max_wait_time)
        except Exception as e:
            # fail if there is any exception
            self.fail(e)

    @classmethod
    def tearDownClass(cls):
        # clean up at the end of the test
        os.system(cls.composeCmd + " down")
        DockerUtil.empty_test_folder("tmp")
