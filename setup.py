from distutils.core import setup


if __name__ == '__main__':
    setup(
        name='starlight_wrapper',
        version='1.2.0',
        author='Bo Zhang',
        author_email='bozhang@nao.cas.cn',
        description='An easy wrapper of STARLIGHT.',  # short description
        license='New BSD',
        # install_requires=['numpy>=1.7','scipy','matplotlib','nose'],
        url='http://github.com/hypergravity/starlight_wrapper',
        classifiers=[
            "Development Status :: 6 - Mature",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2.7",
            "Topic :: Scientific/Engineering :: Astronomy",
            "Topic :: Scientific/Engineering :: Physics"],
        package_dir={'starlight_wrapper': 'starlight_wrapper'},
        packages=['starlight_wrapper'],
        package_data={'starlight_wrapper': ['data/SDSS_DR10/*',
                                            'data/SDSS_DR10/0603/*',
                                            'data/executable/*',
                                            'data/template_mask/*',
                                            'data/template_base/*',
                                            'data/template_base/Base.BC03/*']},
        # include_package_data=True,
        requires=['numpy', 'scipy', 'matplotlib', 'astropy', 'bopy']
    )
