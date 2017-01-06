BROADCAST_FILES = 'BROADCAST_FILES'
LOCAL_FILES = 'LOCAL_FILES'
REMOTE_FILES = 'REMOTE_FILES'
MISSING_FILE = 'MISSING_FILE'
LOAD_FAILED_MESSAGE = 'LOAD_FAILED_MESSAGE'
FILE_REQUEST = 'FILE_REQUEST'
FILE_LOCATION = 'FILE_LOCATION'

SELF_POKE = {'message': 'self-poke'}


def command(message): return message['message']


def broadcast_message(port, files):
    return {
        'message': BROADCAST_FILES,
        'port': port,
        'files': files
    }


def local_files_message(files):
    return {
        'message': LOCAL_FILES,
        'files': files
    }


def remote_files_message(ip, port, files):
    return {
        'message': REMOTE_FILES,
        'ip': ip,
        'port': port,
        'files': files
    }


def missing_file_message(ip, port, missing_file):
    return {
        'message': MISSING_FILE,
        'ip': ip,
        'port': port,
        'file': missing_file
    }


def load_failed_message(missing_file):
    return {
        'message': LOAD_FAILED_MESSAGE,
        'file': missing_file
    }


def file_request_message(file_id):
    return {
        'message': FILE_REQUEST,
        'file_id': file_id
    }
