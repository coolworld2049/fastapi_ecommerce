from setuptools import setup

try:
    # pip >=20
    from pip._internal.network.session import PipSession  # noqa
    from pip._internal.req import parse_requirements  # noqa
except ImportError:
    try:
        # 10.0.0 <= pip <= 19.3.1
        from pip._internal.download import PipSession  # noqa
        from pip._internal.req import parse_requirements  # noqa
    except ImportError:
        # pip <= 9.0.3
        from pip.download import PipSession  # noqa
        from pip.req import parse_requirements  # noqa

version = 'v0.2.3'
package_name = 'fastapi_ecommerce_ext'
url = f'https://github.com/coolworld2049/fastapi-ecommerce/pypi/{package_name}'

install_requires = [str(x.requirement) for x in parse_requirements("requirements.txt", PipSession())]
print(install_requires)
setup(
    name=package_name,
    version=version,
    packages=['fastapi_ecommerce_ext.logger'],
    install_requires=install_requires,
    url=url,
    download_url=f'{url}-{version}.tar.gz',
    license='MIT',
    author='coolworld2049',
    description='logging extension for fastapi-microservices'
)
