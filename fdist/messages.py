BROADCAST_FILES = 'BROADCAST_FILES'
LOCAL_FILES = 'LOCAL_FILES'
REMOTE_FILES = 'REMOTE_FILES'
MISSING_FILE = 'MISSING_FILE'

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
