# actualpy variables - rename this file to config.py
URL_ACTUAL = "http://localhost:5006" # Url of the Actual Server
PASSWORD_ACTUAL = "password" # Password for authentication
ENCRYPTION_PASS_ACTUAL = None,    # Optional: Password for the file encryption. Will not use it if set to None.
FILE_ACTUAL = "Teste" # Set the file to work with. Can be either the file id or file name, if name is unique
DIR_ACTUAL = "./actualpy/temp/" # Optional: Directory to store downloaded files. Will use a temporary if not provided
# CERT_ACTUAL = "<path_to_cert_file>"  # Optional: Path to the certificate file to use for the connection, can also be set as False to disable SSL verification