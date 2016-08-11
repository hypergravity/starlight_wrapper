# -*- coding: utf-8 -*-

"""

Author
------
Bo Zhang

Email
-----
bozhang@nao.cas.cn

Created on
----------
- Thu Aug 11 10:30:00 2016

Modifications
-------------
- Thu Aug 11 10:30:00 2016    create helpers

Aims
----
- some helpers for running STARLIGHT

"""

import os
import numpy as np

def pre_create_dir(filelist, iter=False):
    """ create directories for a list of files

    Parameters
    ----------
    filelist: list
        a list of filepaths
    iter: bool
        whether to iterate the process

    """
    if not iter:
        dirname_list = [os.path.dirname(filepath) for filepath in filelist]
        dirname_u_list = np.unique(dirname_list)
        for dirname_u in dirname_u_list:
            if not os.path.exists(dirname_u):
                os.mkdir(dirname_u)
                print('@Cham: mkdir %s ...' % dirname_u)
    else:
        dirname_list = [os.path.dirname(filepath) for filepath in filelist]
        dirname_u_list = np.unique(dirname_list)
        existence = [os.path.exists(os.path.dirname(dirname_u))
                     for dirname_u in dirname_u_list]
        print(dirname_u_list)
        print(existence)
        if np.all(existence):
            # level 2 dir exists
            for dirname_u in dirname_u_list:
                if not os.path.exists(dirname_u):
                    os.mkdir(dirname_u)
                    print('@Cham: mkdir %s ...' % dirname_u)
        else:
            # need to create level 2 dir
            pre_create_dir(dirname_u_list, iter=iter)
