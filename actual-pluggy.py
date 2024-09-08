from functions import pluggy_sync, backup_actual
import config

try: 
    URL_ACTUAL = config.URL_ACTUAL
    PASSWORD_ACTUAL = config.PASSWORD_ACTUAL
    ENCRYPTION_PASS_ACTUAL = config.ENCRYPTION_PASS_ACTUAL
    FILE_ACTUAL = config.FILE_ACTUAL
    try:
        DIR_ACTUAL = config.DIR_ACTUAL
    except AttributeError:
        pass

    try:
        CERT_ACTUAL = config.CERT_ACTUAL
    except AttributeError:
        pass
except AttributeError:
    print("Erro na definição das configuraçõs do Actual")

backup_actual(URL_ACTUAL, PASSWORD_ACTUAL, FILE_ACTUAL)
pluggy_sync(URL_ACTUAL, PASSWORD_ACTUAL, FILE_ACTUAL)