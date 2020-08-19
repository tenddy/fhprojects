
import tc1
import tc3

TestCases = [True, False, True]


def start(**kargs):
    if TestCases[0]:
        tc1.run()
    if TestCases[2]:
        tc3.run()


if __name__ == "__main__":
    start()
