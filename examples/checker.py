# Copyright (c) 2021 by Kristoffer Paulsson. <kristoffer.paulsson@talenten.se>
from gist.check import ReportBase, check, report

"""The checker.py example is expected to fail with 2 exceptions one ValueError and one RuntimeWarning.
The RuntimeWarning should tell the last executed policy that was started."""


class Evaluation(ReportBase):
    """Evaluating certain policies."""
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


def main():
    evaluatee = Evaluation()
    with report():
        evaluatee.validate()


if __name__ == "__main__":
    main()
