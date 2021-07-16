# Policy Checker

Many developers like to develop systems but are unfortunately very bad at following up bugs as well as documenting business logic.
There is a smart way to combine logging business logic, tracking bugs as well as certifying policy checks at the same time.

It is a reporting system that evaluates policy checks using context managers, context variables, and decorators together to create
an environment where certain business logic can be evaluated at the same time and compiled into a report.

In Python, there is a language construct that makes it easy to create repeatable logic at the same time looking pythonic.

# Reporting base class
First, we need a system to validate a certain number of rules predictably, that's why we need a base class for reporting.
```python
class ReportBase:

    def apply_rules(self) -> bool:
        return any([getattr(self, m)() for m in filter(lambda name: name.startswith("_check_"), dir(self))])

    def validate(self):
        self.apply_rules()
```

The ```ReportBase``` class is a predictable base class that adds a couple of features, by calling ```validate()``` the class will
execute all ```apply_rules()``` methods over the different inherited classes. The apply method will scan each version of the class
for check methods that has the form ```_check_*(self)```, each of these implemented methods will carry out their specific policy check
on appointed business logic.

# Policy context
To collect data from each executed policy check we need to have a collector class, for that we use two things:
* A context variable
* A context manager

When using the context manager we can specify when we want to collect the validation data.

```python
check_ctx = ContextVar("check", default=None)

class report(ContextDecorator):

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
```

The context variable ```check_ctx``` allows the ```report``` decorator to communicate invisibly with the decorated policy checker.
What you do is simply using a ```with``` statement and within it calling all ```validate()``` methods on all business classes you want to use.
Each decorated checker will report its status to the report context. The report context also receives any exceptions while evaluating and reports it
with a specified exception. In this case a ```RuntimeWarning```.

# Policy checker
We have to implement a checker decorator, that triggers the recording mechanism in the decorator so it catches the policy.

```python
def check(policy: str):
    if not policy:
        raise ValueError("Check policy not set!")

    def decorator(func):
        def checker(self, *args, **kwargs):
            checks = check_ctx.get()
            if type(checks) is list:
                checks.append(policy)
            return func(self, *args, **kwargs)
        return checker
    return decorator
```

The decorator is nested so that it can take arguments when it wraps a class method. First, the ```check()``` method will make
sure there is a policy token assigned to the checker, otherwise, the checker policy will not be recorded when applied.
The policy string can be anything that describes what the ```_check_*()``` policy is checking for convenience.

If the check is run outside of policy context the checker will not add any string to the context, otherwise, it will.

# Applying checkers
Now we need to find our business logic and implement the reporting and checkers accordingly.

```python
class Evaluation(ReportBase):

    @check("policy_1")
    def _check_number1(self) -> bool:
        return False

    @check("policy_2")
    def _check_number2(self) -> bool:
        return True

    @check("policy_3")
    def _check_number3(self) -> bool:
        raise ValueError("No value")

    @check("policy_4")
    def _check_number4(self) -> bool:
        return True
```

Each ```_check_*()``` method is decorated with @check and a policy string that names the policy, now we can make a
complete evaluation and reporting of the business logic class.

# Running an evaluation
The validating of the business logic can be used in two ways. You can simply run the validation and explicitly collect all
evaluated business logic, this way it is possible to see if certain requirements of policies have been met.
Also, it is possible to catch the exceptions that go wrong and use the ```RuntimeWarning``` to see all done and the last
started checker by the policy name.

```python
evaluatee = Evaluation()
with report():
    evaluatee.validate()
```

If there is a checker that faults and throws an exception it will be possible to see all started policies.

```python
Traceback (most recent call last):
  File "/examples/checker.py", line 34, in <module>
    main()
  File "/examples/checker.py", line 30, in main
    evaluatee.validate()
  File "/gists/src/gist/check.py", line 23, in __exit__
    raise RuntimeWarning("Checks failed while applying rules in validation.", checks)
RuntimeWarning: ('Checks failed while applying rules in validation.', ['policy_1', 'policy_2', 'policy_3'])
```

This way you easily see which policies were checked in which order and can figure out advanced hard-to-find bugs.

A more advanced policy system is implemented in the [Angelos Project](https://github.com/kristoffer-paulsson/angelos), which is a communication platform that builds on mutual
trust between domains. To trust another domain, certain policies must always comply to be accepted. More can be read on [Medium](https://angelos-project.medium.com).