from setuptools import setup, find_packages


setup(
        name='django-fixture-magic',
        version='0.0.2',
        description='A few extra management tools to handle fixtures.',
        long_description=open('README.rst').read(),
        author='Dave Dash',
        author_email='dd+pypi@davedash.com',
        url='http://github.com/davedash/django-fixture-magic',
        license='BSD',
        packages=find_packages(),
        include_package_data=True,
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Framework :: Django',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )

