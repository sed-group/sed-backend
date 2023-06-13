from tkinter import E


class ProcessNotFoundException(Exception):
    pass


class DSMFileNotFoundException(Exception):
    pass


class EntityRateOutOfOrderException(Exception):
    pass


class FormulaEvalException(Exception):
    def __init__(self, process_id) -> None:
        self.process_id = process_id


class RateWrongOrderException(Exception):
    pass


class NegativeTimeException(Exception):
    def __init__(self, process_id) -> None:
        self.process_id = process_id


class SimulationFailedException(Exception):
    pass


class DesignIdsNotFoundException(Exception):
    pass


class InvalidFlowSettingsException(Exception):
    pass


class VcsFailedException(Exception):
    pass


class BadlyFormattedSettingsException(Exception):
    pass


class FlowProcessNotFoundException(Exception):
  pass
  
class SimSettingsNotFoundException(Exception):
    pass


class NoTechnicalProcessException(Exception):
    pass
