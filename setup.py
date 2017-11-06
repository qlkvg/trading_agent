from setuptools import setup, find_packages

setup(
	name='trading_agent',
	version='0.0.1',
	description='Reckle Trading Agent',
	url='https://github.com/zooliet/trading_agent',
	author='Junhyun Shin',
	author_email='hl1sqi@gmail.com',
	license='MIT',
	packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
	install_requires=['flask', 'flask_json', 'flask-socketio', 'eventlet', 'flask-cors'],
	# install_requires=['flask', 'flask_json', 'flask-socketio', 'flask-cors'],
	include_package_data=True,
)
