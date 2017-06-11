import json
import sys
import timeit

import requests
from .naming import get_name


class Probe:
    def __init__(self, port: int=19876, name: str=None):
        self.root = {
            'children': [],
            'start': timeit.default_timer(),
        }
        self.stack = [self.root]
        self.call = 0
        self.ret = 0
        self.port = port
        self.name = name

    def __enter__(self):
        self.root['start'] = timeit.default_timer()
        sys.setprofile(self._profile)

    def __exit__(self, exc_type, exc_value, traceback):
        sys.setprofile(None)
        self.root['end'] = timeit.default_timer()

        # last one is usually our own __exit__ func
        self.root['children'].pop()

        if not exc_type:
            js = json.dumps(self.root, indent=4)
            requests.post(
                f'http://localhost:{self.port}',
                params={'name': self.name},
                data=js
            )

    def _profile(self, frame, event, arg):
        if event in ['call', 'c_call']:
            self.call += 1

            current = self.stack.pop()
            child = {
                'func': get_name(event, frame, arg),
                'line': frame.f_code.co_firstlineno,
                'file': frame.f_code.co_filename,
                'children': [],
            }
            current['children'].append(child)
            self.stack.append(current)
            self.stack.append(child)
            child['start'] = timeit.default_timer()

        if event in ['return', 'c_return', 'c_exception']:
            self.ret += 1
            end = timeit.default_timer()
            if len(self.stack) > 1:
                current = self.stack.pop()
                current['end'] = end
                current['total'] = current['end'] - current['start']
                current['self'] = current['total'] - sum([child['total'] for child in current['children']])


