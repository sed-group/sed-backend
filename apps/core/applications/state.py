"""
This class maintains the state of all known applications. It is run once during launch, and
provides a set of methods to enable access to known applications. Private variables (underscored variables) should
not be accessed directly.
"""
from typing import List
import json

from fastapi.logger import logger

from apps.core.applications.exceptions import ApplicationNotFoundException
from apps.core.applications.models import Application


# Provide methods to get application data
def get_application_list() -> List[Application]:
    """
    Returns list of all known applications
    :return:
    """
    return _application_list


def get_application(app_id: str) -> Application:
    """
    Returns application instance based on specified application id
    :param app_id:
    :return:
    """
    logger.debug(f"Get application with app_sid = {app_id}")
    if app_id in _applications_data.keys():
        return _get_application_instance(app_id)
    else:
        raise ApplicationNotFoundException


def _get_application_instance(app_id):
    """
    This method serializes the dict formatting of applications to the Applications-class.
    However, to enable fast lookup of any application using id, the dict is not discarded.
    :param app_id:
    :return:
    """
    if app_id not in _applications_data.keys():
        raise ApplicationNotFoundException

    app = Application(
        id=app_id,
        name=_applications_data[key]["name"],
        description=_applications_data[key]["description"],
        href_api=_applications_data[key]["href_api"],
    )

    return app


# Run on module import:
# Open, read, and close applications file
f = open('applications.json', 'r')
_applications_data = json.load(f)           # Loads applications data into a dict object.
f.close()

# Populate list
_application_list = []
for key in _applications_data.keys():
    _application_list.append(_get_application_instance(key))