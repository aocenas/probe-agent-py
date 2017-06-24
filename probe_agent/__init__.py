import os
import json
import sys
import timeit
import psutil
import uuid

import requests
from .naming import get_name

mega = float(2 ** 20)


class Probe:
    def __init__(self, port: int=19876, name: str=None):
        self.uuid = uuid.uuid4()
        self.port = port
        self.name = name
        self.buffer = []

    def __enter__(self):
        sys.setprofile(self._profile)

    def __exit__(self, exc_type, exc_value, traceback):
        sys.setprofile(None)

        self.buffer.append({
            'type': 'end',
            'time': timeit.default_timer(),
        })

        self._push()

    def _profile(self, frame, event, arg):
        if event in ['call', 'c_call', 'return', 'c_return', 'c_exception']:
            event = {
                'type': event,
                'func': get_name(event, frame, arg),
                'line': frame.f_code.co_firstlineno,
                'file': frame.f_code.co_filename,
                'time': timeit.default_timer(),
                'mem': psutil.Process(os.getpid()).memory_info()[0] / mega
            }

            self.buffer.append(event)

            if len(self.buffer) >= 1000:
                self._push()

    def _push(self):
        requests.post(
            f'http://localhost:{self.port}',
            params={
                'name': self.name,
                'uuid': self.uuid,
            },
            data='\n'.join([json.dumps(event) for event in self.buffer])
        )
        self.buffer = []
