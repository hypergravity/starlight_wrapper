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
- Sat Jul 16 22:30:00 2016

Modifications
-------------
- Sat Jul 16 22:30:00 2016    framework
- Sun Jul 17 23:00:00 2016    StarlightGrid
- Mon Jul 18 09:27:00 2016

Aims
----
- to generate config files of STARLIGHT

"""

from __future__ import print_function, division

import os
import copy
import glob
import numpy as np
from astropy.table import Table, Column
from astropy.io import fits
from .config import EXTRA_COMMENTS, PACKAGE_PATH


# ################
# Starlight Grid #
# ################


class StarlightGrid(object):
    """ StarlightGrid class is to represent the Grid file object for STARLIGHT
    """
    # specified order of meta data
    meta_order = ['num_of_fits_to_run',
                  'base_dir',
                  'obs_dir',
                  'mask_dir',
                  'out_dir',
                  'phone_number',
                  'llow_SN',
                  'lupp_SN',
                  'Olsyn_ini',
                  'Olsyn_fin',
                  'Odlsyn',
                  'fscale_chi2',
                  'fit_fxk',
                  'IsErrSpecAvailable',
                  'IsFlagSpecAvailable']
    # default values for StarlightGrid instance
    meta = dict(num_of_fits_to_run=2,
                base_dir='/pool/projects/starlight/STARLIGHTv04/BasesDir/',
                obs_dir='/pool/projects/starlight/STARLIGHTv04/',
                mask_dir='/pool/projects/starlight/STARLIGHTv04/',
                out_dir='/pool/projects/starlight/STARLIGHTv04/',
                phone_number='-2007200',
                llow_SN=4730.0,
                lupp_SN=4780.0,
                Olsyn_ini=3400.0,
                Olsyn_fin=8900.0,
                Odlsyn=1.0,
                fit_fxk='FIT',
                fscale_chi2=1.0,
                IsErrSpecAvailable=1,
                IsFlagSpecAvailable=1)
    # specified order of arq
    arq_order = ['arq_obs',
                 'arq_config',
                 'arq_base',
                 'arq_masks',
                 'red_law_option',
                 'v0_start',
                 'vd_start',
                 'arq_out']
    # default arq data
    arq_obs = []
    arq_config = []
    arq_base = []
    arq_masks = []
    red_law_option = []
    v0_start = []
    vd_start = []
    arq_out = []
    # extra comments
    extra = EXTRA_COMMENTS

    def __init__(self, **kwargs):
        """ initialize instance using arq data """
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])

    def sync_nobs(self):
        """ should sync the n_obs to meta """
        self.meta['num_of_fits_to_run'] = len(self.arq_obs)

    def set_meta(self, **kwargs):
        """ set meta data """
        for key in kwargs.keys():
            self.meta[key] = kwargs[key]

    def is_arq_validate(self):
        """ check if the arq data length validate """
        try:
            n_obs = len(self.arq_obs)
            assert n_obs == len(self.arq_config) \
                or np.isscalar(self.arq_config)
            assert n_obs == len(self.arq_base) \
                or np.isscalar(self.arq_base)
            assert n_obs == len(self.arq_masks) \
                or np.isscalar(self.arq_masks)
            assert n_obs == len(self.red_law_option) \
                or np.isscalar(self.red_law_option)
            assert n_obs == len(self.v0_start) \
                or np.isscalar(self.v0_start)
            assert n_obs == len(self.vd_start) \
                or np.isscalar(self.vd_start)
            assert n_obs == len(self.arq_out)
            return True
        except AssertionError:
            return False

    def pprint_meta(self):
        """ print meta data """
        for key in self.meta_order:
            print("%s: %s" % (key, self.meta[key]))

    def _print_arq_(self, arq_key):
        """ print single arq field data """
        assert arq_key in self.arq_order

        arq_val = self.__getattribute__(arq_key)

        if np.isscalar(arq_val) or len(arq_val) <= 3:
            print(arq_val)
        else:
            print('[%s, %s, ... %s]' % (arq_val[0], arq_val[1], arq_val[-1]))

    def pprint_arq(self):
        """ print all arq data"""
        for key in self.arq_order:
            print("%s:" % key),
            self._print_arq_(key)

    def pprint(self):
        """ print a summary of the instance """
        print("")
        print('StarlightGrid summary:')
        print('############### [meta] ###############')
        self.pprint_meta()
        print('############### [arq]  ###############')
        self.pprint_arq()
        print(self.extra)
        print('######################################')

    def _meta_to_string(self, val_width=50):
        """ convert meta data to string list """
        fmt_str = "%%%ds" % (-val_width)
        return [(fmt_str + "[%s]\n") % (self.meta[key], key)
                for key in self.meta_order]

    def _arq_scalar_to_list(self):
        #  1. arq data to list
        n_obs = len(self.arq_obs)
        for key in self.arq_order:
            val = self.__getattribute__(key)
            if np.isscalar(val):
                self.__setattr__(key, [val for _ in range(n_obs)])
            else:
                assert len(val) == n_obs
        # convert to np.array
        self.__setattr__(key, np.array(self.__getattribute__(key)))

    def _arq_to_string(self, sep='   '):
        """ convert arq data to string list """
        #  1. arq data to list
        n_obs = len(self.arq_obs)
        self._arq_scalar_to_list()

        #  2. to string
        str_list = []
        for i in range(n_obs):
            arq_data_i = ["%s" % self.__getattribute__(key)[i]
                          for key in self.arq_order]
            str_list.append(sep.join(arq_data_i) + "\n")
        return str_list

    def write(self, filepath, meta_val_width=50, sep='   '):
        """ write to filepath in the form of STARLIGHT grid file """
        self.sync_nobs()
        f = open(filepath, "w+")
        f.writelines(self._meta_to_string(meta_val_width))
        f.write('\n')
        f.writelines(self._arq_to_string(sep=sep))
        f.write('\n')
        f.write(self.extra)
        f.close()

    def write_split(self, n_split=24,
                    fmt_str='StarlightGrid%03d.sw', **kwargs):
        """ split self into *n_split* pieces and write to StarlightGrid files
        """
        self.sync_nobs()
        n_obs = self.meta['num_of_fits_to_run']
        # assert n_split > self.meta['num_of_fits_to_run']

        # determine ind
        n_splited = np.int(n_obs) / np.int(n_split) + 1
        n_list = [n_splited for _ in range(n_split)]
        n_list_cs = np.array(np.cumsum(n_list))
        n_list_cs[n_list_cs > n_obs] = n_obs

        # generate multi instance of StarlightGrid
        self._arq_scalar_to_list()

        filepaths = []
        # split self
        for i in range(n_split):
            # filepath
            filepath = fmt_str % (i+1)

            # determine start & stop
            if i == 0:
                ind0 = 0
            else:
                ind0 = n_list_cs[i-1]
            ind1 = n_list_cs[i]

            # possible emtpy StarlightGrid
            if ind0 == ind1:
                print('@Cham: [empty!]: %s' % filepath)
            else:
                filepaths.append(filepath)

            # deep copy
            sg_ = copy.copy(self)

            # set arq
            for arq_key in self.arq_order:
                sg_.__setattr__(arq_key,
                                sg_.__getattribute__(arq_key)[ind0:ind1])

            # write to file
            sg_.write(filepath, **kwargs)

        return filepaths

    def write_split_advanced(self,
                             n_max=None,
                             fmt_str='StarlightGrid_RUN%03d_SUBSET%03d.sw',
                             check_result_existence=False,
                             create_outdir=False,
                             **kwargs):
        """ Split StarlightGrid file to several pieces

        Parameters
        ----------
        n_max: int
            the maximum files will be run
        fmt_str: string
            the format string of the splited StarlightGrid file
        kwargs:

        Returns
        -------
        filepaths: list
            list of splited StarlightGrid files

        """
        # 0. preparation
        self.sync_nobs()
        self._arq_scalar_to_list()

        if check_result_existence:
            ind_exist = [
                os.path.exists(''.join([self.meta['out_dir'], arq_out_]))
                for arq_out_ in self.arq_out]
            ind_use = np.logical_not(np.array(ind_exist))
            print('@Cham: [%s/%s] files will be used ...'
                  % (np.sum(ind_use), len(ind_use)))
            print('@Cham: setting arqs (used only) ...')
            for arq_key in self.arq_order:
                self.__setattr__(
                    arq_key, np.array(self.__getattribute__(arq_key))[ind_use])

        # 1. check dir_obs and dir_out
        file_obs = np.array(
            [self.meta['obs_dir'] + arq_obs_ for arq_obs_ in self.arq_obs])
        file_out = np.array(
            [self.meta['out_dir'] + arq_out_ for arq_out_ in self.arq_out])
        dirname_obs = np.array(
            [os.path.dirname(file_obs_) for file_obs_ in file_obs])
        basename_obs = np.array(
            [os.path.basename(file_obs_) for file_obs_ in file_obs])
        dirname_out = np.array(
            [os.path.dirname(file_out_) for file_out_ in file_out])
        basename_out = np.array(
            [os.path.basename(file_out_) for file_out_ in file_out])
        dirname_obs_out = np.array(
            [dirname_obs_ + dirname_out_
            for dirname_obs_, dirname_out_ in zip(dirname_obs, dirname_out)])
        dirname_obs_out_u, dirname_obs_out_u_id, dirname_obs_out_u_counts \
            = np.unique(dirname_obs_out, return_index=True, return_counts=True)
        # n_dirname_obs_out_u = len(dirname_obs_out_u)
        n_obs = len(file_obs)

        # 2. determine run_id
        run_id = np.zeros(n_obs)
        run_dict = {}
        for i, dirname_obs_out_u_ in enumerate(dirname_obs_out_u):
            run_dict[dirname_obs_out_u_] = i
        for i in range(len(file_obs)):
            run_id[i] = run_dict[dirname_obs_out[i]]

        # 3. write SGs
        filepaths = []
        for i_run, dirname_obs_out_u_ in enumerate(dirname_obs_out_u):
            this_run_ind = np.where(dirname_obs_out==dirname_obs_out_u_)
            # print('this_run_ind')
            # print(this_run_ind)
            # this_run_file_obs = file_obs[this_run_ind]
            # this_run_file_out = file_out[this_run_ind]
            this_run_subs = splitdata_n_max(this_run_ind, n_max)
            # print('this_run_subs')
            # print(this_run_subs)
            this_obs_dir = dirname_obs[this_run_ind[0][0]]
            this_out_dir = dirname_out[this_run_ind[0][0]]

            # mkdir for plate
            if create_outdir:
                if not os.path.exists(this_out_dir):
                    os.mkdir(this_out_dir)
                    print('@Cham: mkdir [%s]' % this_out_dir)

            # write SG for each sub
            for i_sub in range(len(this_run_subs)):
                this_sub_ind = this_run_subs[i_sub]

                filepath = fmt_str % (i_run, i_sub)
                filepaths.append(filepath)

                # deep copy
                sg_ = copy.copy(self)
                # set meta
                sg_.set_meta(obs_dir=this_obs_dir+os.path.sep,
                             out_dir=this_out_dir+os.path.sep)
                # set arq
                for arq_key in self.arq_order:
                    sg_.__setattr__(
                        arq_key, np.array(sg_.__getattribute__(arq_key))[this_sub_ind])
                sg_.arq_obs = basename_obs[this_sub_ind]
                sg_.arq_out = basename_out[this_sub_ind]
                # write to file
                sg_.write(filepath, **kwargs)

                # verbose
                print('@Cham: writing StarlightGrid [%s] (dir=%s, nobs=%d) ...'
                      % (filepath, dirname_obs_out_u_, len(this_sub_ind)))

        print('@Cham: len(self.arq_out) = %s' % len(self.arq_out))
        return filepaths


def splitdata_n_max(data, n_max):
    """ split N into n_max - sized bins """
    data = np.array(data).flatten()
    N = len(data)
    data_splited = []
    for i in range(np.int64(np.ceil(N/n_max))):
        start = i*n_max
        stop  = np.min([(i+1)*n_max, N])
        data_splited.append(data[start:stop])
    return data_splited


def _test_starlight_grid():
    sg = StarlightGrid(arq_obs=['0414.51901.393.cxt',
                                '0784.52327.478.cxt'],
                       arq_config='StCv04.C99.config',
                       arq_base='Base.BC03.N',
                       arq_masks=['Mask.0414.51901.393.cxt.sc1.CRAP.gm.BN',
                                  'Mask.0784.52327.478.cxt.sc2.CRAP.gm.BN'],
                       red_law_option='CCM',
                       v0_start=0.0,
                       vd_start=150.0,
                       arq_out=['0414.51901.393.cxt.sc4.C99.im.CCM.BN',
                                '0784.52327.478.cxt.sc4.C99.im.CCM.BN']
                       )
    sg.pprint_meta()
    sg.pprint_arq()
    sg.pprint()
    for s in sg._meta_to_string():
        print(s)
    for s in sg._arq_to_string(',:'):
        print(s)
    sg.write('/pool/projects/starlight/STARLIGHTv04/grid_example1.in_')


# ################
# Starlight Base #
# ################


class StarlightBase(object):
    """ StarlightBase class is to represent the Base file object for STARLIGHT
    """
    # specified order of meta data
    meta_order = ['n_base']
    # default values for StarlightBase instance
    meta = dict(n_base=45)
    # specified order of arq data
    arq_order = ['spec_file',
                 'age',
                 'z',
                 'code',
                 'mstar',
                 'yav',
                 'afe']
    # default values for bases
    spec_file = []
    age = []
    z = []
    code = []
    mstar = []
    yav = []
    afe = []
    # extra comments
    extra = EXTRA_COMMENTS

    def __init__(self, **kwargs):
        """ initialize instance using arq data """
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])
        # count spec_file
        self.meta['n_base'] = len(self.spec_file)

    def _sync_nbase(self):
        """ synchronize nbase """
        self.meta['n_base'] = len(self.spec_file)

    def _meta_to_string(self, val_width=50):
        """ convert meta data to string list """
        fmt_str = "%%%ds" % (-val_width)
        return [(fmt_str + "[%s]\n") % (self.meta[key], key)
                for key in self.meta_order]

    def _arq_to_string(self, sep='   '):
        """ convert arq data to string list """
        #  1. arq data to list
        n_obs = len(self.spec_file)
        for key in self.arq_order:
            val = self.__getattribute__(key)
            if np.isscalar(val):
                self.__setattr__(key, [val for _ in range(n_obs)])
            else:
                assert len(val) == n_obs

        # 2. to string
        str_list = []
        for i in range(n_obs):
            arq_data_i = ["%s" % self.__getattribute__(key)[i]
                          for key in self.arq_order]
            str_list.append(sep.join(arq_data_i) + "\n")
        return str_list

    def write(self, filepath, meta_val_width=50, sep='   '):
        self._sync_nbase()
        f = open(filepath, "w+")
        f.writelines(self._meta_to_string(meta_val_width))
        # f.write('\n')
        f.writelines(self._arq_to_string(sep))
        f.write('\n')
        f.write(self.extra)
        f.close()

    def quick_set(self,
                  template='Base.BC03.N.dat',
                  template_dir='Base.BC03',
                  copy_base_to=None,
                  **kwargs):
        """ a quick set of StarlightBase """
        # integrated templates
        integrated_templates = ['Base.BC03.N.dat',
                                'Base.BC03.S.dat',
                                'Base.SED.39.dat',
                                'Base.SED.Geneva.sw',
                                'Base.SED.Padova.sw']

        # assert template existence
        template_path = os.path.join(PACKAGE_PATH,
                                     'data',
                                     'template_base',
                                     template)

        # try to read base catalog
        try:
            assert os.path.exists(template_path)
            template_data = Table.read(template_path, **kwargs)
        except AssertionError:
            if template in integrated_templates:
                raise AssertionError(
                    '@Cham: integrated StarlightBase template error!')
            else:
                raise AssertionError(
                    '@Cham: user-defined StarlightBase template error!')

        # assign value
        self.spec_file = template_data['specfile']
        self.age = template_data['age']
        self.z = template_data['Z']
        self.code = template_data['code']
        self.mstar = template_data['Mstar']
        self.yav = template_data['YAV']
        self.afe = template_data['aFe']
        self._sync_nbase()

        # copy base
        self.copy_base_to(src_dir=template_dir, dst_dir=copy_base_to)

    def copy_base_to(self, src_dir='Base.BC03', dst_dir=None):
        # copy base to starlight_dir
        if dst_dir is not None:
            template_dir = os.path.join(PACKAGE_PATH,
                                        'data',
                                        'template_base',
                                        src_dir)
            os.system('cp -r %s %s' % (template_dir, dst_dir))
            print('@Cham: copy template dirctory:\n'
                  'FROM: %s\n'
                  'TO:   %s\n' % (template_dir, dst_dir))


def _test_starlight_base():
    sg = StarlightBase(spec_file=['bc2003_hr_m42_chab_ssp_020.spec',
                                  'bc2003_hr_m42_chab_ssp_045.spec'],
                       age=[0.00100e9,
                            0.00316e9],
                       z=[0.00400,
                          0.00400],
                       code=['age020_m42',
                             'age020_m42'],
                       mstar=[1.0000,
                              0.9999],
                       yav=[0,
                            0],
                       afe=[0.0,
                            0.0]
                       )
    sg.write('/pool/projects/starlight/STARLIGHTv04/Base.BC03.N_')


_config_StCv04C99_ = dict(
    # Normalization lambdas
    l_norm=4020.0,
    llow_norm=4010.0,
    lupp_norm=4060.0,
    # Parameter Limits
    AV_low=-1.0,
    AV_upp=4.0,
    YAV_low=-0.0001,
    YAV_upp=0.0001,
    fn_low=0.7,
    fn_upp=1.3,
    v0_low=-500.0,
    v0_upp=500.0,
    vd_low=0.0,
    vd_upp=500.0,
    # Clipping options & Weight-Control-Filter
    clip_method_option='NSIGMA', # NOCLIP/NSIGMA/RELRES/ABSRES
    sig_clip_threshold=3.0,
    wei_nsig_threshold=2.0,
    # Miscellaneous
    dl_cushion=50.0,
    f_cut=0.001,
    N_int_Gauss=31,
    i_verbose=1,
    i_verbose_anneal=1,
    Is1stLineHeader=0,
    i_FastBC03_FLAG=1,
    i_FitPowerLaw=0,
    alpha_PowerLaw=-0.5,
    i_SkipExistingOutFiles=0,
    # Markov Chains technical parameters
    N_chains=7,
    xinit_max=0.50,
    i_UpdateEps=0,
    i_UpdateAlpha=2,
    Falpha=2.0,
    i_MoveOneParOnly=1,
    i_UpdateAVYAVStepSeparately=1,
    i_HelpParWithMaxR=1,
    prob_jRmax=0.2,
    i_HelpPopVectorMove2Average=1,
    prob_HelpPopVectorMove2Average=0.4,
    i_HelpAVYAVMove2Average=1,
    prob_HelpAVYAVMove2Average=0.4,
    NRC_AV_Default=10,
    # First Fits (FF) technical parameters
    Temp_ini_FF=1.0e2,
    Temp_fin_FF=1.0,
    fini_eps_FF=1.0e1,
    ffin_eps_FF=1.0e2,
    R_ini_FF=1.3,
    R_fin_FF=1.2,
    IsGRTestHard_FF=0,
    N_loops_FF=10,
    i_RestartChains_FF=1,
    fN_sim_FF=1.0e1,
    fNmax_steps_FF=1.0e4,
    eff_IDEAL_FF=0.23,
    # GR R-threshold & Method for Burn-In loop
    R_Burn_in=1.2,
    IsGRTestHard_BurnIn=1,
    # EX0s technical parameters
    EXOs_PopVector_option='MIN', # MIN/AVE
    EXOs_method_option='CUMUL', # CUMUL/SMALL
    EXOs_Threshold=0.02,
    Temp_ini_EX0s=1.0,
    Temp_fin_EX0s=1.0e-3,
    fini_eps_EX0s=1.0e2,
    ffin_eps_EX0s=1.0e3,
    R_ini_EX0s=1.2,
    R_fin_EX0s=1.0,
    IsGRTestHard_EX0s=1,
    N_loops_EX0s=10,
    i_RestartChains_EX0s=1,
    fN_sim_EX0s=1.0e2,
    fNmax_steps_EX0s=1.0e3,
    eff_IDEAL_EX0s=0.50,
    IsScaleNstepsInEX0sFits=1,
    IsNoKin4LargeBaseInEX0sFits=0,
    frac_NoKin4LargeBaseInEX0sFits=0.0,
    fEX0_MinBaseSize=0.1)
_config_StCv04C11_ = dict(
    # Normalization lambdas
    l_norm=4020.0,
    llow_norm=4010.0,
    lupp_norm=4060.0,
    # Parameter Limits
    AV_low=-1.0,
    AV_upp=4.0,
    YAV_low=-0.0001,
    YAV_upp=0.0001,
    fn_low=0.7,
    fn_upp=1.3,
    v0_low=-500.0,
    v0_upp=500.0,
    vd_low=0.0,
    vd_upp=500.0,
    # Clipping options & Weight-Control-Filter
    clip_method_option='NSIGMA',  # NOCLIP/NSIGMA/RELRES/ABSRES
    sig_clip_threshold=3.0,
    wei_nsig_threshold=2.0,
    # Miscellaneous
    dl_cushion=50.0,
    f_cut=0.001,
    N_int_Gauss=31,
    i_verbose=1,
    i_verbose_anneal=0,
    Is1stLineHeader=0,
    i_FastBC03_FLAG=1,
    i_FitPowerLaw=0,
    alpha_PowerLaw=-0.5,
    i_SkipExistingOutFiles=0,
    # Markov Chains technical parameters
    N_chains=7,
    xinit_max=0.50,
    i_UpdateEps=0,
    i_UpdateAlpha=2,
    Falpha=2.0,
    i_MoveOneParOnly=1,
    i_UpdateAVYAVStepSeparately=1,
    i_HelpParWithMaxR=1,
    prob_jRmax=0.2,
    i_HelpPopVectorMove2Average=1,
    prob_HelpPopVectorMove2Average=0.4,
    i_HelpAVYAVMove2Average=1,
    prob_HelpAVYAVMove2Average=0.4,
    NRC_AV_Default=10,
    # First Fits (FF) technical parameters
    Temp_ini_FF=1.0e2,
    Temp_fin_FF=1.0,
    fini_eps_FF=1.0e1,
    ffin_eps_FF=1.0e2,
    R_ini_FF=1.3,
    R_fin_FF=1.3,
    IsGRTestHard_FF=0,
    N_loops_FF=3,
    i_RestartChains_FF=1,
    fN_sim_FF=1.0e1,
    fNmax_steps_FF=1.0e4,
    eff_IDEAL_FF=0.23,
    # GR R-threshold & Method for Burn-In loop
    R_Burn_in=1.2,
    IsGRTestHard_BurnIn=0,
    # EX0s technical parameters
    EXOs_PopVector_option='MIN',  # MIN/AVE
    EXOs_method_option='CUMUL',  # CUMUL/SMALL
    EXOs_Threshold=0.02,
    Temp_ini_EX0s=1.0,
    Temp_fin_EX0s=1.0e-3,
    fini_eps_EX0s=1.0e2,
    ffin_eps_EX0s=1.0e3,
    R_ini_EX0s=1.2,
    R_fin_EX0s=1.0,
    IsGRTestHard_EX0s=1,
    N_loops_EX0s=5,
    i_RestartChains_EX0s=1,
    fN_sim_EX0s=1.0e2,
    fNmax_steps_EX0s=1.0e3,
    eff_IDEAL_EX0s=0.50,
    IsScaleNstepsInEX0sFits=1,
    IsNoKin4LargeBaseInEX0sFits=1,
    frac_NoKin4LargeBaseInEX0sFits=0.0,
    fEX0_MinBaseSize=0.1)

_config_comments_ = (
    ('# Configuration parameters for StarlightChains_v04.for - Cid@Lagoa - 18/Feb/2007 #\n'
     '#\n#\n# Normalization lambdas\n#\n'),
    '#\n#\n# Parameter Limits\n#\n',
    '#\n#\n# Clipping options & Weight-Control-Filter\n#\n',
    '#\n#\n# Miscellaneous\n#\n',
    '#\n#\n# Markov Chains technical parameters\n#\n',
    '#\n#\n# First Fits (FF) technical parameters\n#\n',
    '#\n#\n# GR R-threshold & Method for Burn-In loop\n#\n',
    '#\n#\n# EX0s technical parameters\n#\n',
    (
        '\n\nCid@Lagoa - 18/February/2007'
        '\n\nOBS: A SLOW config!'
        '\n\n\n\n'
        'Technical parameters you may want to play with to obtain FAST, MEDIUM'
        '\n& SLOW fits:\n\n'
        '--------------------------------\n'
        '|  FAST  |    MEDIUM  |  LONG  |\n'
        '--------------------------------\n'
        '|  5     |    7       |  12    | [N_chains]\n'
        '|  3     |    5       |  10    | [N_loops_FF & *_EX0s]\n'
        '|  1.3   |    1.2     |  1.1   | [R_ini_FF & R_fin_FF & *_EX0s]\n'
        '|  0     |   0 or 1   |  1     | [IsGRTestHard_FF & *_BurnIn & *_EX0s]\n'
        '--------------------------------\n')
    )
_config_comments_insert_index_ = (
    0, 4, 15, 19, 30, 45, 58, 61, 65)


# ##################
# Starlight Config #
# ##################


class StarlightConfig(object):
    """ StarlightConfig class is to represent the Config file object for STARLIGHT
    """
    # specified order of meta data
    meta_order = [
        # Normalization lambdas
        'l_norm',
        'llow_norm',
        'lupp_norm',
        # Parameter Limits
        'AV_low',
        'AV_upp',
        'YAV_low',
        'YAV_upp',
        'fn_low',
        'fn_upp',
        'v0_low',
        'v0_upp',
        'vd_low',
        'vd_upp',
        # Clipping options & Weight-Control-Filter
        'clip_method_option',
        'sig_clip_threshold',
        'wei_nsig_threshold',
        # Miscellaneous
        'dl_cushion',
        'f_cut',
        'N_int_Gauss',
        'i_verbose',
        'i_verbose_anneal',
        'Is1stLineHeader',
        'i_FastBC03_FLAG',
        'i_FitPowerLaw',
        'alpha_PowerLaw',
        'i_SkipExistingOutFiles',
        # Markov Chains technical parameters
        'N_chains',
        'xinit_max',
        'i_UpdateEps',
        'i_UpdateAlpha',
        'Falpha',
        'i_MoveOneParOnly',
        'i_UpdateAVYAVStepSeparately',
        'i_HelpParWithMaxR',
        'prob_jRmax',
        'i_HelpPopVectorMove2Average',
        'prob_HelpPopVectorMove2Average',
        'i_HelpAVYAVMove2Average',
        'prob_HelpAVYAVMove2Average',
        'NRC_AV_Default',
        # First Fits (FF) technical parameters
        'Temp_ini_FF',
        'Temp_fin_FF',
        'fini_eps_FF',
        'ffin_eps_FF',
        'R_ini_FF',
        'R_fin_FF',
        'IsGRTestHard_FF',
        'N_loops_FF',
        'i_RestartChains_FF',
        'fN_sim_FF',
        'fNmax_steps_FF',
        'eff_IDEAL_FF',
        # GR R-threshold & Method for Burn-In loop
        'R_Burn_in',
        'IsGRTestHard_BurnIn',
        # EX0s technical parameters
        'EXOs_PopVector_option',
        'EXOs_method_option',
        'EXOs_Threshold',
        'Temp_ini_EX0s',
        'Temp_fin_EX0s',
        'fini_eps_EX0s',
        'ffin_eps_EX0s',
        'R_ini_EX0s',
        'R_fin_EX0s',
        'IsGRTestHard_EX0s',
        'N_loops_EX0s',
        'i_RestartChains_EX0s',
        'fN_sim_EX0s',
        'fNmax_steps_EX0s',
        'eff_IDEAL_EX0s',
        'IsScaleNstepsInEX0sFits',
        'IsNoKin4LargeBaseInEX0sFits',
        'frac_NoKin4LargeBaseInEX0sFits',
        'fEX0_MinBaseSize']
    # default values for StarlightConfig instance (StCv04.C99.config)
    meta = _config_StCv04C99_
    # extra comments
    extra = EXTRA_COMMENTS
    # necessary comments
    config_comments = _config_comments_
    config_comments_insert_index = _config_comments_insert_index_

    def __init__(self, **kwargs):
        """ initialize StarlightConfig instance with StCv04.C99.config """
        self.set_meta(**kwargs)

    def set_meta(self, **kwargs):
        """ set meta data """
        for key in kwargs.keys():
            assert key in self.meta.keys()
            self.meta[key] = kwargs[key]

    def set_quick(self, template='StCv04.C99.config'):
        if template == 'StCv04.C99.config':
            self.set_meta(**_config_StCv04C99_)
        elif template == 'StCv04.C11.config':
            self.set_meta(**_config_StCv04C11_)
        else:
            raise(ValueError('@Cham: your option should be one of {''StCv04.C99.config'', ''StCv04.C11.config''}'))

    def _meta_to_string(self, val_width=50):
        """ convert meta data to string list """
        fmt_str = "%%%ds" % (-val_width)
        return [(fmt_str + "[%s]\n") % (self.meta[key], key)
                for key in self.meta_order]

    def write(self, filepath, meta_val_width=50):
        f = open(filepath, "w+")
        str_list = self._meta_to_string(meta_val_width)

        # insert necessary comments
        for i in range(len(self.config_comments_insert_index)-1):
            str_list.insert(
                self.config_comments_insert_index[i], self.config_comments[i])
        str_list.append(self.config_comments[-1])

        # for str in str_list:
        #     print(str)

        f.writelines(str_list)
        f.write('\n')
        f.write(self.extra)
        f.close()


def _test_starlight_config():
    sc = StarlightConfig()
    sc.set_quick('StCv04.C99.config')
    print(sc.meta)
    sc.set_quick('StCv04.C11.config')
    print(sc.meta)
    sc.set_meta(Is1stLineHeader=1)
    sc.write('/pool/projects/starlight/STARLIGHTv04/StCv04.C99.config_')


# ################
# Starlight Mask #
# ################


class StarlightMask(Table):
    """ StarlightMask class is to represent the Mask file object for STARLIGHT
    """

    def __init__(self):
        super(self.__class__, self).__init__(
            data=[[], [], [], [], []],
            names=['wave1', 'wave2', 'mask_value', 'comment', 'sky'],
            dtype=['f8', 'f8', 'f8', 'S70', '?'],
            masked=True)

    def quick_set(self, template='sm_tplt.sdss_gm.fits'):
        """ a quick set to Starlight Mask template """
        # integrated templates
        integrated_templates = ['sm_tplt.sdss_gm.fits',
                                'sm_tplt.bc03_short.fits',
                                'sm_tplt.bc03_long.fits']

        # assert template existence
        template_path = os.path.join(PACKAGE_PATH,
                                     'data',
                                     'template_mask',
                                     template)
        try:
            assert os.path.exists(template_path)
            template_data = Table.read(template_path)
        except AssertionError:
            if template in integrated_templates:
                raise AssertionError(
                    '@Cham: integrated StarlightMask template error!')
            else:
                raise AssertionError(
                    '@Cham: user-defined StarlightMask template error!')

        # clean
        self.clean()

        # fill self with template
        for _ in template_data:
            self.add_row(_)

    def clean(self):
        """ clean all items in a StarlightMask instance """
        while len(self) > 0:
            self.remove_row(0)

    def _to_string(self, sep='  ', z=None):
        """ convert to string list """
        if self['sky'].data.any():
            # need redshift to calculate the wavelength
            assert z is not None

        str_list = []
        for i in range(len(self)):
            if self['sky'][i]:
                str_list.append('%s%s%s%s%s%s%s%s%s\n'
                                % (self['wave1'][i]/(1+z), sep,
                                   self['wave2'][i]/(1+z), sep,
                                   self['mask_value'][i], sep,
                                   self['comment'][i], sep,
                                   self['sky'][i]))
            else:
                str_list.append('%s%s%s%s%s%s%s%s%s\n'
                                % (self['wave1'][i], sep,
                                   self['wave2'][i], sep,
                                   self['mask_value'][i], sep,
                                   self['comment'][i], sep,
                                   self['sky'][i]))
        return str_list

    def write_to(self, filepath, z=None, sep='  '):
        """ write mask in STARLIGHT form """
        f = open(filepath, 'w+')
        f.write('%d\n' % len(self))
        f.writelines(self._to_string(sep=sep, z=z))
        f.write(EXTRA_COMMENTS)
        f.close()


def _test_starlight_mask():
    sm = StarlightMask()
    sm.quick_set('sdss_gm')
    sm.quick_set('bc03_short')
    sm.add_row([6280, 6288, 2, 'DIB6284', 0])
    sm.add_row([5567, 5587, 0, 'skyline', 1])
    sm.pprint()
    sm.write_to('/pool/projects/starlight/STARLIGHTv04/Masks.EmLines.SDSS.gm_', z=0.01)


# ##################
# Starlight Output #
# ##################


class StarlightOutput(object):
    """ StarlightOutput class is to read/re-construct the STARLIGHT results
    """
    meta = dict(
        arq_obs='',
        arq_base='',
        arq_masks='',
        arq_config='',
        N_base=0,
        N_YAV_components=0,
        i_FitPowerLaw=0,
        alpha_PowerLaw=0,
        red_law_option='',
        q_norm=0,
        l_ini=0.,
        l_fin=0.,
        dl=0.,
        l_norm=0.,
        llow_norm=0.,
        lupp_norm=0.,
        fobs_norm=0.,
        llow_SN=0.,
        lupp_SN=0.,
        SN_in_SN_window=0.,
        SN_in_norm_window=0.,
        SN_err_in_SN_window=0.,
        SN_err_in_norm_window=0.,
        fscale_chi2=0.,
        idum_orig=0,
        NOl_eff=0,
        Nl_eff=0,
        Ntot_cliped=0,
        clip_method='',
        Nglobal_steps=0,
        N_chains=0,
        NEX0s_base=0,
        Clip_Bug=0,
        RC_Crash=0,
        Burn_In_warning_flags=0,
        n_censored_weights=0,
        wei_nsig_threshold=0,
        wei_limit=0,
        idt_all=0,
        wdt_TotTime=0.,
        wdt_UsrTime=0.,
        wdt_SysTime=0.,
        chi2_Nl_eff=0.,
        adev=0.,
        sum_of_x=0.,
        Flux_tot=0.,
        Mini_tot=0.,
        Mcor_tot=0.,
        v0_min=0.,
        vd_min=0.,
        AV_min=0.,
        YAV_min=0.)
    syn_spec = None
    syn_model = None

    def __init__(self, filepath):
        """ initialize instance

        Parameters
        ----------
        filepath: string
            file path of the starlight output

        Returns
        -------
        so: StarlightOutput instance
            StarlightOutput instance

        """
        # assert filepath existence
        try:
            assert os.path.exists(filepath)
        except AssertionError:
            raise(AssertionError('@Cham: file does not exist! %s' % filepath))

        # read header
        f = open(filepath, 'r')
        lines = f.readlines()
        self.meta, state = read_starlight_output_header(lines)
        f.close()
        try:
            assert state
        except AssertionError:
            raise(AssertionError('@Cham: starlight read header FAILED!'))

        # read blocks
        # As pointed out by the STARLIGHT manual, 3 out of 5 blocks are ignored
        # Only the synthetic results (coefficients [1/5] and spectra [5/5])
        # are loaded into data

        # 1. syn model
        N_base = self.meta['N_base']
        self.syn_model = read_starlight_output_syn_model(lines[63:63+N_base])

        # 2. syn spectrum
        syn_spec_start = 63+N_base+5+N_base+2+N_base+11
        Nl_obs = np.int(lines[syn_spec_start-1].split('[')[0].strip())
        # assert that the number of rest lines is equal to Nl_obs
        assert len(lines) - syn_spec_start == Nl_obs
        self.syn_spec = read_starlight_output_syn_spec(lines[syn_spec_start:])

    def pprint(self):
        len_max = np.max([len(key) for key in self.meta.keys()])
        fmt_str = '%%%ds' % (len_max+1)
        for k,v in self.meta.items():
            print((fmt_str+': %s') % (k, v))
        print('')
        print(self.syn_model)
        print('')
        print(self.syn_spec)

    def write_fits(self, filepath, **kwargs):
        # replace nan/inf values in meta dict with -999.
        for k, v in self.meta.items():
            if np.isnan(v) or np.isinf(v):
                self.meta[k] = -999.

        # construct fits Primary HDU
        prihdr = fits.Header()
        prihdr['AUTHOR'] = 'Bo Zhang'
        for k, v in self.meta.items():
            prihdr[k] = v
        prihdu = fits.PrimaryHDU(header=prihdr)

        # construct fits HDU list
        hdulist = fits.HDUList([prihdu,
                                fits.table_to_hdu(self.syn_model),
                                fits.table_to_hdu(self.syn_spec)])
        if os.path.exists(filepath):
            print('[StarlightOuput.write_fits()]: filepath exists: %s'
                  % filepath)
        hdulist.writeto(filepath, **kwargs)


def read_starlight_output_syn_spec(lines):
    """ read syn_spec of starlight output """
    Nl_obs = len(lines)
    wave = Column(np.zeros((Nl_obs, ), dtype=np.float), 'wave')
    flux_obs = Column(np.zeros((Nl_obs, ), dtype=np.float), 'flux_obs')
    flux_syn = Column(np.zeros((Nl_obs, ), dtype=np.float), 'flux_syn')
    weight = Column(np.zeros((Nl_obs, ), dtype=np.float), 'weight')
    for i, line in enumerate(lines):
        line_split = line.split()
        wave[i] = np.float(line_split[0])
        flux_obs[i] = np.float(line_split[1])
        flux_syn[i] = np.float(line_split[2])
        weight[i] = np.float(line_split[3])
    return Table([wave, flux_obs, flux_syn, weight])


def read_starlight_output_syn_model(lines):
    """ read syn_model of starlight output """
    N_base=len(lines)
    j = Column(np.zeros((N_base,), dtype=np.int), 'j')
    x_j = Column(np.zeros((N_base,), dtype=np.float), 'x_j')
    Mini_j = Column(np.zeros((N_base,), dtype=np.float), 'Mini_j')
    Mcor_j = Column(np.zeros((N_base,), dtype=np.float), 'Mcor_j')
    age_j = Column(np.zeros((N_base,), dtype=np.float), 'age_j')
    Z_j = Column(np.zeros((N_base,), dtype=np.float), 'Z')
    LM_j = Column(np.zeros((N_base,), dtype=np.float), 'LM_j')
    YAV = Column(np.zeros((N_base,), dtype=np.float), 'YAV')
    Mstars = Column(np.zeros((N_base,), dtype=np.float), 'Mstars')
    component_j = Column(np.zeros((N_base,), dtype=np.string_), 'component_j')
    aFe = Column(np.zeros((N_base,), dtype=np.float), 'aFe')
    SSP_chi2r = Column(np.zeros((N_base,), dtype=np.float), 'SSP_chi2r')
    SSP_adev = Column(np.zeros((N_base,), dtype=np.float), 'SSP_adev')
    SSP_AV = Column(np.zeros((N_base,), dtype=np.float), 'SSP_AV')
    SSP_x = Column(np.zeros((N_base,), dtype=np.float), 'SSP_x')
    for i in range(len(lines)):
        line_split = lines[i].split()
        j[i] = np.int(line_split[0])
        x_j[i] = np.float(line_split[1])
        Mini_j[i] = np.float(line_split[2])
        Mcor_j[i] = np.float(line_split[3])
        age_j[i] = np.float(line_split[4])
        Z_j[i] = np.float(line_split[5])
        LM_j[i] = np.float(line_split[6])
        YAV[i] = np.float(line_split[7])
        Mstars[i] = np.float(line_split[8])
        component_j[i] = line_split[9]
        aFe[i] = np.float(line_split[10])
        SSP_chi2r[i] = np.float(line_split[11])
        SSP_adev[i] = np.float(line_split[12])
        SSP_AV[i] = np.float(line_split[13])
        SSP_x[i] = np.float(line_split[14])
    return Table([j, x_j, Mini_j, Mcor_j, age_j, Z_j, LM_j, YAV, Mstars,
                  component_j, aFe, SSP_chi2r, SSP_adev, SSP_AV, SSP_x])


def read_starlight_output_header(lines):
    """ read header of starlight output
    Although this method is not elegant, it works!
    """
    # initial state False
    state = False
    # initialize meta
    meta = dict()
    try:
        # Some input info
        meta['arq_obs'] = lines[5].split('[')[0].strip()
        meta['arq_base'] = lines[6].split('[')[0].strip()
        meta['arq_masks'] = lines[7].split('[')[0].strip()
        meta['arq_config'] = lines[8].split('[')[0].strip()
        meta['N_base'] = np.int(lines[9].split('[')[0].strip())
        meta['N_YAV_components'] = np.int(lines[10].split('[')[0].strip())
        meta['i_FitPowerLaw'] = np.int(lines[11].split('[')[0].strip())
        meta['alpha_PowerLaw'] = np.float(lines[12].split('[')[0].strip())
        meta['red_law_option'] = lines[13].split('[')[0].strip()
        meta['q_norm'] = np.float(lines[14].split('[')[0].strip())
        # (Re)Sampling Parameters
        meta['l_ini'] = np.float(lines[17].split('[')[0].strip())
        meta['l_fin'] = np.float(lines[18].split('[')[0].strip())
        meta['dl'] = np.float(lines[19].split('[')[0].strip())
        # Normalization info
        meta['l_norm'] = np.float(lines[22].split('[')[0].strip())
        meta['llow_norm'] = np.float(lines[23].split('[')[0].strip())
        meta['lupp_norm'] = np.float(lines[24].split('[')[0].strip())
        meta['fobs_norm'] = np.float(lines[25].split('[')[0].strip())
        # S/N
        meta['llow_SN'] = np.float(lines[28].split('[')[0].strip())
        meta['lupp_SN'] = np.float(lines[29].split('[')[0].strip())
        meta['SN_in_SN_window'] = np.float(lines[30].split('[')[0].strip())
        meta['SN_in_norm_window'] = np.float(lines[31].split('[')[0].strip())
        meta['SN_err_in_SN_window'] = np.float(lines[32].split('[')[0].strip())
        meta['SN_err_in_norm_window'] =\
            np.float(lines[33].split('[')[0].strip())
        meta['fscale_chi2'] = np.float(lines[34].split()[0].strip('['))
        # etc... [ignored ugly data form! --> this makes me happy!]
        meta['NOl_eff'] = np.int(lines[38].split('[')[0].strip())
        meta['Nl_eff'] = np.int(lines[39].split('[')[0].strip())
        lines_40_split = lines[40].split('[')[0].strip().split()
        meta['Ntot_cliped'] = np.float(lines_40_split[0])
        meta['clip_method'] = lines_40_split[1]
        meta['Nglobal_steps'] = np.int(lines[41].split('[')[0].strip())
        meta['N_chains'] = np.int(lines[42].split('[')[0].strip())
        meta['NEX0s_base'] = np.int(lines[43].split('[')[0].strip())
        # Synthesis Results - Best model
        meta['chi2_Nl_eff'] = np.float(lines[49].split('[')[0].strip())
        meta['adev'] = np.float(lines[50].split('[')[0].strip())
        meta['sum_of_x'] = np.float(lines[52].split('[')[0].strip())
        meta['Flux_tot'] = np.float(lines[53].split('[')[0].strip())
        meta['Mini_tot'] = np.float(lines[54].split('[')[0].strip())
        meta['Mcor_tot'] = np.float(lines[55].split('[')[0].strip())
        meta['v0_min'] = np.float(lines[57].split('[')[0].strip())
        meta['vd_min'] = np.float(lines[58].split('[')[0].strip())
        meta['AV_min'] = np.float(lines[59].split('[')[0].strip())
        meta['YAV_min'] = np.float(lines[60].split('[')[0].strip())
    except Exception:
        return meta, state
    state = True
    return meta, state


def _test_read_starlight_output_header():
    f = open('/pool/projects/starlight/STARLIGHTv04/'
             '0414.51901.393.cxt.sc4.C99.im.CCM.BN_11')
    lines = f.readlines()
    f.close()
    meta, state = read_starlight_output_header(lines)
    print(state)
    print(meta)


def _test_starlight_output():
    filepath = ('/pool/projects/starlight/STARLIGHTv04/'
                '0414.51901.393.cxt.sc4.C99.im.CCM.BN_11')
    so = StarlightOutput(filepath)
    so.pprint()
    so.write_fits('/pool/projects/starlight/STARLIGHTv04/'
                  '0414.51901.393.cxt.sc4.C99.im.CCM.BN_11.fits',
                  clobber=True)


if __name__ == '__main__':
    # _test_starlight_grid()
    # _test_starlight_base()
    # _test_starlight_config()
    # _test_starlight_mask()
    # _test_read_starlight_output_header()
    # _test_starlight_output()
    _test_starlight_mask()