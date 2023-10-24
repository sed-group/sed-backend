from tkinter import E
import re


class ProcessNotFoundException(Exception):
    pass


class DSMFileNotFoundException(Exception):
    pass


class EntityRateOutOfOrderException(Exception):
    pass


class FormulaEvalException(Exception):
    def __init__(self, exception, sim_data) -> None:
        self.name = sim_data['iso_name'] if sim_data['iso_name'] is not None else sim_data['sub_name']
        pattern = r"found '([^']+)'"
        match = re.search(pattern, str(exception))
        if match:
            found_char = match.group(1)
            self.message = f"Check your formula for \"{found_char}\""
        else:
            self.message = str(exception)


class RateWrongOrderException(Exception):
    pass


class NegativeTimeException(Exception):
    def __init__(self, sim_data) -> None:
        self.name = sim_data['iso_name'] if sim_data['iso_name'] is not None else sim_data['sub_name']


class SimulationFailedException(Exception):
    def __init__(self, exception) -> None:
        self.message = str(exception)


class DesignIdsNotFoundException(Exception):
    pass


class InvalidFlowSettingsException(Exception):
    pass


class VcsFailedException(Exception):
    pass


class BadlyFormattedSettingsException(Exception):
    def __init__(self, message) -> None:
        self.message = message


class FlowProcessNotFoundException(Exception):
  pass
  
class SimSettingsNotFoundException(Exception):
    pass


class NoTechnicalProcessException(Exception):
    pass


class CouldNotFetchSimulationDataException(Exception):
    pass


class CouldNotFetchMarketInputValuesException(Exception):
    pass


class CouldNotFetchValueDriverDesignValuesException(Exception):
    pass
