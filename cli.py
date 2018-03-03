#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CLI App."""
import datetime
import getpass
import os

from blessings import Terminal

from fuzzyfinder import fuzzyfinder
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import confirm
from pyactivecollab import ActiveCollab, Config

t = Terminal()


class FuzzyCompleter(Completer):
    """Fuzzy Completer Alpha Sorted."""

    def __init__(self, words):
        """Initialize."""
        self.words = words

    def get_completions(self, document, complete_event):
        """Use fuzzyfinder for completions."""
        word_before_cursor = document.text_before_cursor
        words = fuzzyfinder(word_before_cursor, self.words)
        for x in words:
            yield Completion(x, -len(word_before_cursor))


class DateFuzzyCompleter(Completer):
    """Fuzzy Completer For Dates."""

    def get_completions(self, document, complete_event):
        """Use fuzzyfinder for date completions.

        The fuzzyfind auto sorts by alpha so this is to show dates relative to
        the current date instead of by day of week.
        """
        base = datetime.datetime.today()
        date_format = '%a, %Y-%m-%d'
        date_list = [(base - datetime.timedelta(days=x)).strftime(date_format)
                     for x in range(0, 30)]
        word_before_cursor = document.text_before_cursor
        words = fuzzyfinder(word_before_cursor, date_list)

        def sort_by_date(date_str: str):
            return datetime.datetime.strptime(date_str, date_format)

        # Re-sort by date rather than day name
        words = sorted(words, key=sort_by_date, reverse=True)
        for x in words:
            yield Completion(x, -len(word_before_cursor))


class WeekFuzzyCompleter(Completer):
    """Fuzzy Completer For Weeks."""

    def get_completions(self, document, complete_event):
        """Use fuzzyfinder for week completions."""
        def datetime_to_week_str(dt: datetime.datetime):
            """Convert a datetime to weekstring.

            datetime.datetime(2018, 2, 26, 0, 0) => '2018-02-26 to 2018-03-04'
            """
            if dt.weekday() != 0:
                monday_dt = dt - datetime.timedelta(days=dt.weekday())
            sunday_dt = monday_dt + datetime.timedelta(days=6)
            return '{} to {}'.format(
                monday_dt.strftime('%Y-%m-%d'), sunday_dt.strftime('%Y-%m-%d'))

        base = datetime.datetime.today()
        week_list = [datetime_to_week_str(base - datetime.timedelta(weeks=x))
                     for x in range(0, 5)]
        word_before_cursor = document.text_before_cursor
        words = fuzzyfinder(word_before_cursor, week_list)
        words = sorted(words, reverse=True)
        for x in words:
            yield Completion(x, -len(word_before_cursor))


def timestamp_to_datetime(json, fieldname):
    """Convert field from timestamp to datetime for json.

    Currenlty hardcoded to MST timezone
    """
    timestamp = json[fieldname]
    mst_hours = datetime.timedelta(hours=7)
    json[fieldname] = datetime.datetime.fromtimestamp(timestamp) + mst_hours
    return json


def create_time_record(ac):
    """Super Innefficient calls to create a time record."""
    # Get Project
    projects = ac.get_projects()
    suggestions = [x['name'] for x in projects]
    completer = FuzzyCompleter(suggestions)
    text = prompt('(Project)> ', completer=completer)
    project = next(x for x in projects if x['name'] == text)
    # Value
    value = prompt('(Value)> ')
    # If integer is passed then treat it as minutes
    if ('.' not in value) and (':' not in value):
        value = float(value) / 60
    # Job Type
    job_types = ac.get_job_types()
    suggestions = [x['name'] for x in job_types]
    completer = FuzzyCompleter(suggestions)
    text = prompt('(Job Type)> ', completer=completer)
    job_type = next(x for x in job_types if x['name'] == text)
    # Date
    completer = DateFuzzyCompleter()
    text = prompt('(Date)> ', completer=completer)
    choosen_date = datetime.datetime.strptime(text, '%a, %Y-%m-%d')
    # Billable
    billable_choices = {True: 1, False: 0}
    billable = confirm('(Billable (y/n))> ')
    billable = billable_choices[billable]
    # Summary
    summary = prompt('(Summary)> ', enable_open_in_editor=True)
    # User
    users = ac.get_users()
    user = next(x for x in users if x['email'] == config.user)
    data = {
        'value': value,
        'user_id': user['id'],
        'job_type_id': job_type['id'],
        'record_date': choosen_date.strftime('%Y-%m-%d'),
        'billable_status': billable,
        'summary': summary
    }
    url = '/projects/{}/time-records'.format(project['id'])
    ac.post(url, data)


def list_daily_time_records(ac):
    """List current user's time entrys for a specific day."""
    os.system('cal -3')
    # Make sure that the input is valid. This should be broken out to
    # encapsulate all auto-complete inputs
    completer = DateFuzzyCompleter()
    valid = False
    while not valid:
        try:
            date_str = prompt('(Date)> ', completer=completer)
            choosen_date = datetime.datetime.strptime(date_str, '%a, %Y-%m-%d')
        except ValueError:
            print('Bad input, try again.')
        else:
            valid = True
    users = ac.get_users()
    user = next(x for x in users if x['email'] == config.user)
    r = ac.get_time_records(user['id'])
    time_records = r['time_records']
    time_records = [timestamp_to_datetime(x, 'record_date') for x in time_records]
    daily_time_records = [x for x in time_records
                          if x['record_date'].date() == choosen_date.date()]
    billable = 0
    non_billable = 0
    daily_hours = 0
    for record in daily_time_records:
        if record['billable_status']:
            print(t.green('{:<6} {}'.format(record['value'], record['summary'][:60])))
            billable += record['value']
        else:
            print(t.blue('{:<6} {}'.format(record['value'], record['summary'][:60])))
            non_billable += record['value']
        daily_hours += record['value']
    print((t.yellow(str(daily_hours)) + ' ' +
           t.green(str(billable)) + ' ' +
           t.blue(str(non_billable))))


def list_weekly_time_records(ac):
    """List current user's time entrys for a specific week."""
    os.system('cal -3')
    # Make sure that the input is valid. This should be broken out to
    # encapsulate all auto-complete inputs
    completer = WeekFuzzyCompleter()
    valid = False
    while not valid:
        try:
            week_str = prompt('(Week)> ', completer=completer)
            monday_dt = datetime.datetime.strptime(week_str.split()[0], '%Y-%m-%d')
            sunday_dt = datetime.datetime.strptime(week_str.split()[2], '%Y-%m-%d')
        except ValueError:
            print('Bad input, try again.')
        else:
            valid = True
    users = ac.get_users()
    user = next(x for x in users if x['email'] == config.user)
    r = ac.get_time_records(user['id'])
    time_records = r['time_records']
    time_records = [timestamp_to_datetime(x, 'record_date') for x in time_records]
    weekly_time_records = [x for x in time_records if
                           x['record_date'].date() >= monday_dt.date() and
                           x['record_date'].date() <= sunday_dt.date()]
    days = [(sunday_dt - datetime.timedelta(days=x)) for x in range(7)]
    weekly_billable = 0
    weekly_non_billable = 0
    weekly_hours = 0
    for day in days:
        billable = 0
        non_billable = 0
        daily_hours = 0
        if day.date() > datetime.datetime.now().date():
            continue
        daily_time_records = [x for x in weekly_time_records if
                              x['record_date'].date() == day.date()]
        print(day)
        for record in daily_time_records:
            if record['billable_status']:
                print(t.green('{:<6} {}'.format(record['value'], record['summary'][:60])))
                billable += record['value']
                weekly_billable += record['value']
            else:
                print(t.blue('{:<6} {}'.format(record['value'], record['summary'][:60])))
                non_billable += record['value']
                weekly_non_billable += record['value']
            daily_hours += record['value']
            weekly_hours += record['value']
        print((t.yellow(str(daily_hours)) + ' ' +
               t.green(str(billable)) + ' ' +
               t.blue(str(non_billable))))
    print('Weekly Hours')
    print((t.yellow(str(weekly_hours)) + ' ' +
           t.green(str(weekly_billable)) + ' ' +
           t.blue(str(weekly_non_billable))))
    print('Percent Billable: {:.2f}%'.format(100 - ((37.5-weekly_billable)/37.5*100)))


# Load config, ensure password
config = Config()
config.load()
if not config.password:
    config.password = getpass.getpass()

ac = ActiveCollab(config)
ac.authenticate()
actions = {
    'Create Time Record': create_time_record,
    'List Daily Time Records': list_daily_time_records,
    'List Weekly Time Records': list_weekly_time_records,
}
completer = FuzzyCompleter(actions.keys())
while True:
    action = prompt('(Action)> ', completer=completer)
    actions[action](ac)
