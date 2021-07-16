# Copyright (c) 2021 by Kristoffer Paulsson. <kristoffer.paulsson@talenten.se>
"""A way of checking and collecting policies on objects so that they can be easily reported."""
from contextlib import ContextDecorator
from contextvars import ContextVar


check_ctx = ContextVar("check", default=None)


class report(ContextDecorator):
    """Collects reports last time a @check with a set policy was done."""

    def __init__(self):
        self._token = check_ctx.set(list())

    def __enter__(self):
        return check_ctx.get()

    def __exit__(self, *exc):
        checks = check_ctx.get()
        check_ctx.reset(self._token)
        if exc:
            raise RuntimeWarning("Checks failed while applying rules in validation.", checks)
        return False


def check(policy: str):
    """Check policy decorator."""
    if not policy:
        raise ValueError("Check policy not set!")

    def decorator(func):
        """Method decorator."""
        def checker(self, *args, **kwargs):
            """Policy checker."""
            checks = check_ctx.get()
            if type(checks) is list:
                checks.append(policy)
            return func(self, *args, **kwargs)
        return checker
    return decorator


class ReportBase:
    """Base class for validation enabled policies."""

    def apply_rules(self) -> bool:
        return any([getattr(self, m)() for m in filter(lambda name: name.startswith("_check_"), dir(self))])

    def validate(self):
        self.apply_rules()