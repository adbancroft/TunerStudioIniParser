from setuptools import setup

setup(name='TsIniParser',
      version='0.6',
      description='A parser for TunerStudio INI files',
      url='https://github.com/adbancroft/TunerStudioIniParser',
      author='adbancroft',
      author_email='13982343+adbancroft@users.noreply.github.com',
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Text Processing',
      ],
      license='LGPL',
      packages=['TsIniParser', 'TsIniParser.dataclasses'],
      package_dir={'TsIniParser': 'ts_ini_parser'},
      package_data={'TsIniParser': ['grammars/*.lark', 'grammars/*.lark.cache']},
      install_requires=[
          'lark-parser'
      ],
      zip_safe=False)
