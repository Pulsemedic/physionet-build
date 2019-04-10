from os import walk, chdir, listdir, path

from google.api_core.exceptions import BadRequest
from google.cloud import storage

import logging

logger = logging.getLogger(__name__)
Public_Roles = ['roles/storage.legacyBucketReader', 'roles/storage.legacyObjectReader',
    'roles/storage.objectViewer']

def check_bucket(project, version):
    """
    Function to check if a bucket already exists 
    """
    storage_client = storage.Client()
    bucket_name = '{0}-{1}.physionet.org'.format(project.lower(), version)
    exists = storage_client.lookup_bucket(bucket_name)
    if exists:
        return True
    return False

def create_bucket(project, version, protected=False):
    """
    Function to create a bucket and set its permissions
    """
    storage_client = storage.Client()
    bucket_name = '{0}-{1}.physionet.org'.format(project, version)
    bucket = storage_client.create_bucket(bucket_name)
    logger.info("Created bucket {0} for project {1}".format(bucket_name.lower(), project))
    if not protected:
        make_bucket_public(bucket)
    else:
        remove_bucket_permissions(bucket)
    return bucket_name

def make_bucket_public(bucket):
    """
    Function to make a bucket public to all users 
    """
    bucket.iam_configuration.bucket_policy_only_enabled = True
    bucket.patch()
    policy = bucket.get_iam_policy()
    for role in Public_Roles:
        policy[role].add('allUsers')
    bucket.set_iam_policy(policy)
    logger.info("Made bucket {} public".format(bucket.name))

def remove_bucket_permissions(bucket):
    """
    Function to remove all permissions from bucket but owner 
    """
    policy = bucket.get_iam_policy()
    To_remove = []
    for role in policy:
        if role != 'roles/storage.legacyBucketOwner':
            for member in policy[role]:
                To_remove.append([role, member])
    for item in To_remove:
        policy[item[0]].discard(item[1])
    if To_remove:
        bucket.set_iam_policy(policy)
        logger.info("Removed all read permissions from bucket {}".format(bucket.name))

def add_email_bucket_access(project, email):
    """
    Function to add access to a bucket from a email 
    If the email is elegible to be used in GCP the set iam policy will pass
    If not, it will return a error as a bad requet.
    """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(project.gcp.bucket_name)
    policy = bucket.get_iam_policy()
    for role in Public_Roles:
        policy[role].add('user:'+email)
    try:
        bucket.set_iam_policy(policy)
        logger.info("Added email {0} to the project {1} access list".format(
            email, project))
    except BadRequest: 
        logger.info("There was an error on the request. The email {} was ignored.".format(
            email))

def upload_files(project):
    """
    Function to send files to a bucket. Gets a list of all the 
    files under the project root directory then it sends each file 
    one by one. The only way to know if the zip file is created is to 
    heck the compressed sotrage size. If the zip is created, then send it.
    """
    file_root = project.file_root()
    subfolders_fullpath = [x[0] for x in walk(file_root)]
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(project.gcp.bucket_name)
    for indx, location in enumerate(subfolders_fullpath):
        chdir(location)
        files = [f for f in listdir('.') if path.isfile(f)]
        for file in files:
            temp_dir = location.replace(file_root,'')
            if temp_dir != '':
                blob = bucket.blob(path.join(temp_dir, file)[1:])
                blob.upload_from_filename(file)
            else:
                blob = bucket.blob(file)
                blob.upload_from_filename(file)
    if project.compressed_storage_size:
        zip_name = project.zip_name()
        chdir(project.project_file_root())
        blob = bucket.blob(zip_name)
        blob.upload_from_filename(zip_name)

## Unused functions but usefull information.
def set_bucket_permissions(bucket_name, email):
    """
    Function to set the permissions of a bucket to a specific group
    if ACL are used. At the moment we deal with bucket level permissions. 
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    bucket.acl.group(email).grant_read()
    bucket.acl.save()

def list_bucket_permissions(bucket):
    """
    Function to list all the permissions of a bucket.
    """
    policy = bucket.get_iam_policy()
    for role in policy:
        members = policy[role]
        print('Role: {}, Members: {}'.format(role, members))
