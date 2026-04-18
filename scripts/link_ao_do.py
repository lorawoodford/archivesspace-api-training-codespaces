import argparse
import asnake.logging as logging
import sys

from asnake.aspace import ASpace
from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from datetime import datetime

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("-rId", "--repo-id", help="repo id for new resource", type=int)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()

def link_matching():
    any_found = False

    for ao in repo.archival_objects:
        matching_do = aspace_client.get(f'{repo.uri}/find_by_id/digital_objects?digital_object_id[]={ao.ref_id}').json()
        if do := matching_do['digital_objects']:
            do_uri = do[0]['ref']
            link_do(ao, do_uri)
            any_found = True
    if not any_found:
        print(f'No archival object ref_ids in {repo.uri} match any digital object ids.')
        logger.info(f'No archival object ref_ids in {repo.uri} match any digital object ids.')

def link_do(ao, do_uri):
    if not args.dry_run:
        doInstance = {}
        doInstance['digital_object'] = {'ref': do_uri}
        doInstance['instance_type'] = 'digital_object'

        ao = aspace_client.get(ao.uri).json()
        ao['instances'].append(doInstance)
        ao_response = aspace_client.post(ao['uri'], json=ao)
        print(f'New digital object instance added to archival object: {ao_response.json()}')
        logger.info(f'New digital object instance added to archival object: {ao_response.json()}')
    else:
        print(f'The following digital object would be attached as an instance to {ao.uri}: ', do_uri)
        logger.info(f'The following digital object would be attached as an instance to {ao.uri}: {do_uri}')

def main(dry_run=False):
    try:
        global aspace_client
        aspace_client = ASnakeClient()
        aspace_client.authorize()
    except ASnakeAuthError as e:
        print('Failed to authorize ASnake client', e)
        raise ASnakeAuthError
    
    global repo 
    repo = ASpace().repositories(args.repo_id)
    
    link_matching()

if __name__ == "__main__":
    global args
    args = parseArguments()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logging.setup_logging(filename=f"./logs/my_log_{timestamp}.log", level="DEBUG")
    logger = logging.get_logger('updateAoDoLog')

    print(f'Running {sys.argv[0]} script with following arguments: ')
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        print(str(arg) + ": " + str(args.__dict__[arg]))
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))

    main(dry_run=args.dry_run)