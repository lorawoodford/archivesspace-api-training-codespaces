import argparse
import asnake.logging as logging
import sys

from asnake.aspace import ASpace
from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from datetime import datetime
from waybackpy import WaybackMachineCDXServerAPI
from waybackpy.exceptions import NoCDXRecordFound

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("-rId", "--repo-id", help="repo id for new resource", type=int)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()

def get_web_aos():
    aos = [ao for ao in repo.search.with_params(q='primary_type:archival_object AND extent_type_enum_s:"web archives"') or []]
    print(f'{len(aos)} web archive archival object(s) found in repository {repo.id}')
    logger.info(f'{len(aos)} web archive archival object(s) found in repository {repo.id}')
    for ao in aos:
        get_wayback_link(ao)

def get_wayback_link(ao):
    try:
        cdx_api = WaybackMachineCDXServerAPI(ao.title)
        newest = cdx_api.newest()
        if newest:
            build_do(ao, newest)
    except NoCDXRecordFound:
        print(f'No archived page found for {ao.title}')
        logger.info(f'No archived page found for {ao.title}')
    except Exception as e:
        print(f'An error occurred: {e}')
        logger.info(f'An error occurred: {e}')

def build_do(ao, newest):
    doid = newest.archive_url

    # Search to see if DO already exists
    for do in repo.search.with_params(q=f'primary_type:digital_object AND digital_object_id:"{doid}"'):
        print(f'A digital object matching this archive url {doid} already exists: {do.uri}')
        logger.info(f'A digital object matching this archive url {doid} already exists: {do.uri}')
        return

    print(f'Building digital object for {doid}.')
    logger.info(f'Building digital object for {doid}.')
    doPost = {}
    doPost['digital_object_id'] = doid
    doPost['title'] = f'Web crawl of {ao.title}'
    doPost['publish'] = True
    doPost['dates'] = [{'expression': newest.timestamp, 'date_type': 'single', 'label': 'creation'}]
    doPost['file_versions'] = [{'file_uri': doid,'publish': True,'file_size_bytes': int(newest.length),'checksum': newest.digest,'checksum_method': 'sha-1'}]
    
    create_and_link_do(ao, doPost)

def create_and_link_do(ao, doPost):
    if not args.dry_run:
        do_response = aspace_client.post(f'{repo.uri}/digital_objects', json=doPost)
        print(f'New digital object created: {do_response.json()}')
        logger.info(f'New digital object created: {do_response.json()}')

        if do_response and do_response.status_code == 200:
            doInstance = {}
            doInstance['digital_object'] = {'ref': do_response.json()['uri']}
            doInstance['instance_type'] = 'digital_object'

            ao = aspace_client.get(ao.uri).json()
            ao['instances'].append(doInstance)
            ao_response = aspace_client.post(ao['uri'], json=ao)
            print(f'New digital object instance added to archival object: {ao_response.json()}')
            logger.info(f'New digital object instance added to archival object: {ao_response.json()}')
    else:
        print(f'The following digital object would be created and attached as an instance to {ao.uri}: ', doPost)
        logger.info(f'The following digital object would be created and attached as an instance to {ao.uri}: {doPost}')

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

    get_web_aos()

if __name__ == '__main__':
    global args
    args = parseArguments()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logging.setup_logging(filename=f"./logs/my_log_{timestamp}.log", level="DEBUG")
    logger = logging.get_logger('waybackLog')

    print(f'Running {sys.argv[0]} script with following arguments: ')
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        print(str(arg) + ": " + str(args.__dict__[arg]))
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(dry_run=args.dry_run)
