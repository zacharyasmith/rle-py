import logging

logger = logging.getLogger()


class LDBoard:
    def __init__(self):
        self.passing = True
        self.test_status = dict()

    def results(self):
        """
        Processes test status dictionary in its current state.
        :return: multiline string of test results
        """
        ret_val = 'Passing: {}\n'.format(self.passing)
        for n in self.test_status.keys():
            ret_val += '\t{}: {}\n'.format(n, 'passed' if self.test_status[n] else 'failed')
        return ret_val

    def process_test_result(self, name, result):
        """
        Processes result by updating status dictionary
        :param name: Name of the test
        :param result: Boolean result
        """
        self.test_status[name] = result
        self.passing = self.passing if result else False
        logger.info('Test {} resulted: {}'.format(name, 'passed' if result else 'failed'))
