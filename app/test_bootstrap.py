import sys
import types

# Stub boto3
boto3 = types.ModuleType("boto3")
sys.modules.setdefault("boto3", boto3)

# Stub botocore and common submodules boto3 expects
botocore = types.ModuleType("botocore")
exceptions = types.ModuleType("botocore.exceptions")

# Add a dummy ClientError so imports like:
# from botocore.exceptions import ClientError
# do not fail
class ClientError(Exception):
    pass

exceptions.ClientError = ClientError

sys.modules.setdefault("botocore", botocore)
sys.modules.setdefault("botocore.exceptions", exceptions)
