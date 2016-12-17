BROADCAST_LOCAL_FILES = 'BROADCAST_LOCAL_FILES'
LOCAL_FILES = 'LOCAL_FILES'
REMOTE_FILES = 'REMOTE_FILES'
MISSING_FILES = 'MISSING_FILES'

SELF_POKE = {'message': 'self-poke'}


def broadcast_message(ip, port, files):
    return {
        'message': BROADCAST_LOCAL_FILES,
        'ip': ip,
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


def missing_file_message(ip, port, file):
    return {
        'message': MISSING_FILES,
        'ip': ip,
        'port': port,
        'file': file
    }
