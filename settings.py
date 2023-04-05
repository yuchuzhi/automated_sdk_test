import os

os.path.abspath(__file__)
LOCAL_SCRIPT = os.path.dirname(os.path.abspath(__file__))
APP_TEST_PATH = os.path.join(LOCAL_SCRIPT, "app_test").replace("\\", "/")
CONFIGURATION_PATH = os.path.join(LOCAL_SCRIPT, "config/config.xml")
