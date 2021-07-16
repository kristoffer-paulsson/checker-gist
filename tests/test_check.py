# Copyright (c) 2021 by Kristoffer Paulsson. <kristoffer.paulsson@talenten.se>
import unittest

from gist.check import ReportBase, check, report


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


class CheckerText(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.evaluatee = Evaluation()

    def test_report(self):
        with self.assertRaises(RuntimeWarning):
            with report():
                self.evaluatee.validate()


if __name__ == "__main__":
    unittest.main()