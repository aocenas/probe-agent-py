from setuptools import setup

setup(
    name='probe-agent',
    version='1.0.0',
    description='Probe agent',
    url='http://github.com/aocenas/probe-agent-agent-py',
    author='Andrej Ocenas',
    author_email='mr.ocenas@gmail.com',
    license='MIT',
    packages=['probe_agent'],
    install_requires=[
        'requests',
    ],
    keywords=['perf', 'monitoring', 'profiling'],
    zip_safe=False
)
