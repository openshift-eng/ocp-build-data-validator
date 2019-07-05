import setuptools

setuptools.setup(
    name='rh-ocp-build-data-validator',
    author='AOS ART Team',
    author_email='aos-team-art@redhat.com',
    version='0.0.7',
    description='Validation of ocp-build-data Image & RPM declarations',
    long_description=open('README.rst').read(),
    url='https://gitlab.cee.redhat.com/openshift-art/tools/ocp-build-data-validator',  # noqa: E501
    license='Red Hat Internal',
    packages=['validator', 'validator.schema'],
    entry_points={'console_scripts': [
        'validate-ocp-build-data = validator.__main__:main'
    ]},
    include_package_data=True,
    install_requires=['pyyaml', 'schema', 'requests'])
