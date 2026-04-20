import argparse
import asnake.logging as logging
import json
import sys

from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from datetime import datetime

def parseArguments():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-rId", "--repo-id", help="repo id for new resource", type=int)
    parser.add_argument("-reT", "--resource-title", help="title of new resource", type=ascii)
    parser.add_argument("-reId", "--resource-id", help="id0 of new resource", type=ascii)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()

def build_resource(resource_title, resource_id):
    my_resource = {}
    my_resource['title'] = resource_title.strip('"\'')
    my_resource['id_0'] = resource_id.strip('"\'')

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
    
    return my_resource

def main(repo_id, resource_title, resource_id, dry_run=False):
    try:
        aspace_client = ASnakeClient()
        aspace_client.authorize()
    except ASnakeAuthError as e:
        print('Failed to authorize ASnake client', e)
        raise ASnakeAuthError

    if not dry_run:
        response = aspace_client.post(f'/repositories/{repo_id}/resources', json=build_resource(resource_title, resource_id))

        print("Status Code:", response.status_code)
        print("Response Body:", response.text)
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Body: {json.loads(response.text)}")
    else:
        draft_resource = build_resource(resource_title, resource_id)
        print("The following resource would be created:", draft_resource)
        logger.info(f"The following resource would be created: {draft_resource}")

if __name__ == '__main__':
    args = parseArguments()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logging.setup_logging(filename=f"./logs/postResourceV2_{timestamp}.log", level="DEBUG")
    logger = logging.get_logger('postResourceLog')

    print(f'Running {sys.argv[0]} script with following arguments: ')
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        print(str(arg) + ": " + str(args.__dict__[arg]))
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(repo_id=args.repo_id, resource_title=args.resource_title, resource_id=args.resource_id, dry_run=args.dry_run)
