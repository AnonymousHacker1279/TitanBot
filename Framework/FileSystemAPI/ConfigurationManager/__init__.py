from Framework.GeneralUtilities import GeneralUtilities
from .ConfigurationManager import ConfigurationManager

configuration_manager = ConfigurationManager()
GeneralUtilities.run_and_get(configuration_manager.load_core_config())
