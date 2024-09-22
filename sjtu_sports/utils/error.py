# TODO: Define exceptions here

ErrorCode_kOk = 0
# Request
ErrorCode_kMethodNotAllowed = 1
ErrorCode_kInvalidSession = 2
# API
ErrorCode_kLoginExpired = 100
ErrorCode_kInvalidOrder = 101
ErrorCode_kFieldTypeNotFound = 102
ErrorCode_kInvalidFieldMeta = 103

ErrorCode_kUnknown = 199

ErrorCode_name = {
    0: "kOk",
    1: "kMethodNotAllowed",
    2: "kInvalidSession",

    100: "kLoginExpired",
    101: "kInvalidOrder",
    102: "kFieldTypeNotFound",
    103: "kInvalidFieldMeta",
    199: "kUnknown"
}

class OttoError(Exception):
    def __init__(self, error_code, message=None):
        self.error_code = error_code
        self.message = message
    
    def __str__(self) -> str:
        return f"OttoError: err={ErrorCode_name[self.error_code]}, msg={self.message}"
