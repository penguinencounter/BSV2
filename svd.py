from globals import timeout_transport
from studentvue import StudentVue
from requests.exceptions import ConnectTimeout
from math import floor
import copy
import time


class Gradebook:
    def __init__(self, reporting_period_data: dict):
        self.report_periods = reporting_period_data
        self.raw_gradebook_data = {}
    
    def fetch(self, sv: StudentVue):
        for k in self.report_periods.keys():
            start = time.time()
            print(f'Gradebook: download period {k} ... ', end='', flush=True)
            self.raw_gradebook_data[k] = sv.get_gradebook(k)
            end = time.time()
            print(f'done in {floor((end-start)*10)/10}s', flush=True)


class StudentVueContainer:
    def __init__(self, username: str, password: str, domain: str):
        self.username = username
        self.password = password
        self.domain = domain
        self.active_sv = None
        self.gradebook = None
        self.report_periods = {}

    def create_sv(self, retries=5):
        retries_available = copy.copy(retries)
        while retries_available > 0:
            print(f'Attempting to create a StudentVue instance for {self.username}...')
            try:
                self.active_sv = StudentVue(self.username, self.password, self.domain, zeep_transport=timeout_transport)
            except ConnectTimeout:
                print(f'Timed out: {retries_available} retries left')
                retries_available -= 1
            else:
                print(f'Created a StudentVue instance for {self.username}.')
                return True
        return False

    def verify_has_sv(self, caller=None):
        if self.active_sv is None:
            print(f'Calling <{caller}> requires an active StudentVue object, creating one now...')
            self.create_sv()
        return self.active_sv

    def get_reporting_periods(self):
        self.verify_has_sv('get_reporting_periods')
        start = time.time()
        print('Downloading grade-period data...')
        report_periods = self.active_sv.get_gradebook()['Gradebook']['ReportingPeriods']['ReportPeriod']
        for period in report_periods:
            self.report_periods[period['@Index']] = dict(period)
        end = time.time()
        print(f'get_reporting_periods: done in {floor((end-start)*10)/10}s')

    def get_gradebook(self):
        self.verify_has_sv('get_gradebook')
        if len(self.report_periods) == 0:
            print(f'No reporting period data found; attempting autopopulation')
            self.get_reporting_periods()
        self.gradebook = Gradebook(self.report_periods)
        self.gradebook.fetch(self.active_sv)
        
