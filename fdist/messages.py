BROADCAST_FILES = 'BROADCAST_FILES'
LOCAL_FILES = 'LOCAL_FILES'
REMOTE_FILES = 'REMOTE_FILES'
MISSING_FILE = 'MISSING_FILE'
LOAD_FAILED_MESSAGE = 'LOAD_FAILED_MESSAGE'
FILE_REQUEST = 'FILE_REQUEST'
FILE_INFO = 'FILE_INFO'
PIP_REQUEST = 'PIP_REQUEST'
PIP_DATA = 'PIP_DATA'

SELF_POKE = {'message': 'self-poke'}
SUCCESS_MESSAGE = {'message': 'success'}
FAILURE_MESSAGE = {'message': 'failure'}
_file_id_key = 'file_id'


def command(message): return message['message']


def file_id_of(message): return message[_file_id_key]


def broadcast_message(port, files): return {
    'message': BROADCAST_FILES,
    'port': port,
    'files': files
}


def local_files_message(files): return {
    'message': LOCAL_FILES,
    'files': files
}


def remote_files_message(ip, port, files): return {
    'message': REMOTE_FILES,
    'ip': ip,
    'port': port,
    'files': files
}


def missing_file_message(ip, port, missing_file_id): return {
    'message': MISSING_FILE,
    'ip': ip,
    'port': port,
    _file_id_key: missing_file_id
}


def load_failed_message(missing_file_id): return {
    'message': LOAD_FAILED_MESSAGE,
    _file_id_key: missing_file_id
}


def accept_connection_message(connection, ip, parsed_message=''): return {
    'connection': connection,
    'ip': ip,
    'parsed': parsed_message
}


def file_request_message(file_id): return {
    'message': FILE_REQUEST,
    _file_id_key: file_id
}


def file_info_message(file_id, pip_length, hashes): return {
    'message': FILE_INFO,
    _file_id_key: file_id,
    'pip_length': pip_length,
    'hashes': hashes
}


def pip_request_message(file_id, required_indices): return {
    'message': PIP_REQUEST,
    _file_id_key: file_id,
    'required_indices': required_indices
}


def pip_message(pip_ix, data): return {
    'message': PIP_DATA,
    'pip_ix': pip_ix,
    'data': data
}
