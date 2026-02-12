from sigmatch import (
    SignatureError,
    SignatureMismatchError,
    SignatureNotFoundError,
    UnsupportedSignatureError,
)


def test_inheritance():
    assert issubclass(SignatureMismatchError, SignatureError)
    assert issubclass(SignatureNotFoundError, SignatureError)
    assert issubclass(UnsupportedSignatureError, SignatureError)
