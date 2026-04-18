import argparse
import asnake.logging as logging
import csv
import requests
import sys

from asnake.aspace import ASpace
from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from datetime import datetime

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("csvPath", help="path to csv input file", type=str)
    parser.add_argument("-rId", "--repo-id", help="repo id for new resource", type=int)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()

def read_csv(filename, encoding_type='UTF-8'):
    try:
        open_csv = open(filename, 'r', encoding=encoding_type)
        return csv.DictReader(open_csv)
    except FileNotFoundError:
        logger.error(f"Error: The file '{filename}' was not found.")
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)
    except PermissionError:
        logger.error(f"Error: Permission denied to access '{filename}'.")
        print(f"Error: Permission denied to access '{filename}'.")
        sys.exit(1)
    except csv.Error as e:
        logger.error(f"CSV Error: {e}")
        print(f"CSV Error: {e}")
        sys.exit(1)

def check_url(url):
    try:
        response = requests.head(url)
        if response.status_code == 200:
            return True
        else:
            logger.error(f"The url '{url}' returned a non-200 status code and will not be updated.  Status code: {response.status_code}.")
            print(f"The url '{url}' returned a non-200 status code and will not be updated.  Status code: {response.status_code}.")
    except requests.exceptions.RequestException as e:
        logger.error(f'Trouble fetching the new url: {e}. The url will not be updated.')
        print(f'Trouble fetching the new url: {e}. The url will not be updated.')
    
def build_digital_object(do, new_uri):
    do['file_versions'][0]['file_uri'] = new_uri
    return do

def update_digital_object(do):
    do_response = aspace_client.post(do['uri'], json=do)
    print(f'Digital object updated: {do_response.json()}')
    logger.info(f'Digital object updated: {do_response.json()}')

def main(updated_file_uri_csv, dry_run=False):
    try:
        global aspace_client
        aspace_client = ASnakeClient()
        aspace_client.authorize()
    except ASnakeAuthError as e:
        print('Failed to authorize ASnake client', e)
        raise ASnakeAuthError
    
    global repo 
    repo = ASpace().repositories(args.repo_id)
    
    csv_dict = read_csv(updated_file_uri_csv)
    for obj in csv_dict:
        digital_object_id = obj['digital_object_id']
        new_uri = obj['updated_file_uri']
        if check_url(new_uri):
            do = aspace_client.get(f'{repo.uri}/digital_objects/{digital_object_id}').json()
            if 'error' not in do:
                data = build_digital_object(do, new_uri)
                if not dry_run:
                    update_digital_object(do)
                else:
                    message = (
                        f"Digital object {digital_object_id} would be updated with the following data:\n"
                        f"{data}"
                    )
                    logger.info(message)
                    print(message)
            else:
                print(f'Digital object {digital_object_id} not found.')
                logger.info(f'Digital object {digital_object_id} not found.')

if __name__ == "__main__":
    global args
    args = parseArguments()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logging.setup_logging(filename=f"./logs/my_log_{timestamp}.log", level="DEBUG")
    logger = logging.get_logger('updateFileuriLog')

    print(f'Running {sys.argv[0]} script with following arguments: ')
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        print(str(arg) + ": " + str(args.__dict__[arg]))
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))

    main(args.csvPath, dry_run=args.dry_run)