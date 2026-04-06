import asnake.logging as logging

from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logging.setup_logging(filename=f"./logs/my_log_{timestamp}.log", level="DEBUG")

try:
    aspace_client = ASnakeClient()
    aspace_client.authorize()
    # print(aspace_client.get('repositories').json())
except ASnakeAuthError as e:
    print('Failed to authorize ASnake client', e)
    raise ASnakeAuthError

my_repo = ""

my_resource = {}
my_resource['title'] = ""
my_resource['id_0'] = ""

my_resource['level'] = "collection"
my_resource['finding_aid_language'] = "eng"
my_resource['finding_aid_script'] = "Latn"
my_resource['dates'] = [
    {
        "expression": "1900-2000",
        "date_type": "inclusive",
        "label": "creation",
        "jsonmodel_type": "date"
    }
]
my_resource['extents'] = [
    {
        "number": "1",
        "portion": "whole",
        "extent_type": "linear_feet",
        "jsonmodel_type": "extent"
    }
]
my_resource['lang_materials'] = [
    {
        "jsonmodel_type": "lang_material"
    }
]
language_and_script = {
    "language": "eng",
    "jsonmodel_type": "language_and_script"
}
my_resource['lang_materials'][0]['language_and_script'] = language_and_script

response = aspace_client.post(f'/repositories/{my_repo}/resources', json=my_resource)

# Print response details
print("Status Code:", response.status_code)
print("Response Body:", response.text)

# Raise error if request failed
response.raise_for_status()
