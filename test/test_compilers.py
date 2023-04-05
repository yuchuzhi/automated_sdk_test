from unittest import TestCase
from mcutool.compilers import factory
from mcutool.compilers import compilerfactory

class TestCompiler(TestCase):
    def test_mcux_info(self):
        mcux_module = compilerfactory("mcux")
        mcux_path, version = mcux_module.get_latest_tool()
        mcux = mcux_module(mcux_path, version=version)
        assert mcux.path
        print(mcux.version)
        print(mcux.name)

    def test_armgcc_info(self):
        armgcc_module = compilerfactory("armgcc")
        armgcc_path, version = armgcc_module.get_latest_tool()
        armgcc = armgcc_module(armgcc_path, version=version)
        assert armgcc.path
        print(armgcc.version)
        print(armgcc.name)

