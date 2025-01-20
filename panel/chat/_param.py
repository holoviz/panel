from param import Parameter


class CallbackException(Parameter):
    """
    A Parameter type to validate callback_exception options. Supports
    "raise", "summary", "verbose", "traceback", "ignore", or a callable.
    """

    def __init__(self, default="summary", **params):
        super().__init__(default=default, **params)
        self._validate(default)

    def _validate(self, val):
        self._validate_value(val, self.allow_None)

    def _validate_value(self, val, allow_None, valid=("raise", "summary", "verbose", "traceback", "ignore")):
        if ((val is None and allow_None) or val in valid or callable(val)):
            return
        raise ValueError(
            f"Callback exception mode {val} not recognized. "
            f"Valid options are {valid} or a callable."
        )
