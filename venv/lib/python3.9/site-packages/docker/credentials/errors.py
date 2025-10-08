class StoreError(RuntimeError):
    pass


class CredentialsNotFound(StoreError):
    pass


class InitializationError(StoreError):
    pass


def process_store_error(cpe, program):
    message = cpe.output.decode('utf-8')
    if 'credentials not found in native keychain' in message:
        return CredentialsNotFound(f'No matching credentials in {program}')
    return StoreError(f'Credentials store {program} exited with "{message}".')
