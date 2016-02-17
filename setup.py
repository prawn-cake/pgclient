from distutils.core import setup

setup(
    name='pgclient',
    version='0.2.3',
    packages=['pgclient'],
    install_requires=['psycopg2'],
    url='https://github.com/prawn-cake/pgclient',
    license='MIT',
    author='Maksim Ekimovskii',
    author_email='ekimovsky.maksim@gmail.com',
    description='Yet another psycopg2 wrapper'
)
