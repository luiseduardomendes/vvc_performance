import pandas as pd
from .vvc_output import VVC_Output
from ..common.commonlib import bdr_calc
import numpy as np
from scipy import interpolate, integrate
import math
import matplotlib.pyplot as plt


class BD_Rate(pd.Series):
    __indexes__ = ['version','video','cfg','frame']
    __name__    = 'bd-rate'
    __version__ = None
    __video__   = None
    __cfg__     = None
    __nqps__    = 4

    def __init__(self, version = None, video = None, cfg = None, nqps=4):
        self.__version__ = version
        self.__video__   = video
        self.__cfg__     = cfg
        self.__nqps__    = nqps

        super().__init__([], name=self.__name__, index=self.__mk_empty_index__(), dtype=float)

    def plot_bdr_video(self, video, savefig=False, figname='bdr_data.png'):
        df = self[:,video,:, -1]
        index = df.index
        versions = set()
        indexes = set()
        for i in index:
            version, cfg = i
            versions.add(version)
            indexes.add(cfg)
        values = {}
        indexes = list(indexes)
        indexes
        for version in versions:
            values[version] = np.asarray(df[version,:])

        bar_width = 1/len(versions)*0.9

        r = []
        r.append(np.arange(len(indexes)))
        for i in range(1, len(versions)):
            r.append(np.array([x + bar_width for x in r[i-1]]))

        plt.figure(figsize=(10, 6))
        for i, version in enumerate(versions):
            plt.bar(r[i], values[version], width=bar_width, edgecolor='grey', label=version)
        plt.xlabel('Configuration Parameter')
        plt.ylabel('BD Rate')
        plt.title(f'Rate Distortion Comparison between Approximate computation\nVersions for \"{video}\" video')
        plt.xticks([r_ + bar_width/2 for r_ in range(len(indexes))], indexes)
        plt.legend()

        if savefig:
            plt.savefig(f'bdr_{video}.png')
        else:
            plt.show()


    def calc_bdbr(self, cmp_df : VVC_Output, ref_df : VVC_Output):
        cmp_df = cmp_df.sort_values(by=['frame', 'qp'])
        ref_df = ref_df.sort_values(by=['frame', 'qp']) 
        bdr = [
            bdr_calc(
                cmp_df.iloc[i:i+self.__nqps__], 
                ref_df.iloc[i:i+self.__nqps__]
            ) 
            for i in range(0, len(cmp_df['frame']), self.__nqps__)
        ]
        
        index = self.__mk_index__(
            self.__version__, 
            self.__video__, 
            self.__cfg__, 
            cmp_df, 
            self.__nqps__
        )
        super().__init__(bdr, name=self.__name__, index=index, dtype=float)
        return self

    def append_bd(self, bd_rate):
        super().__init__(pd.concat([self, bd_rate]))

    def __mk_empty_index__(self) -> pd.MultiIndex:
        return pd.MultiIndex.from_arrays(
            [[], [], [], [],], names=self.__indexes__
        )

    def __mk_index__(self, satd, video, cfg, cmp_df, qps) -> pd.MultiIndex:
        temp = np.array(cmp_df['frame'])
        index = pd.MultiIndex.from_arrays(
            [
                [
                    satd
                    for i in range(0, len(cmp_df['frame']), qps)
                ],
                [
                    video
                    for i in range(0, len(cmp_df['frame']), qps)
                ],
                [
                    cfg
                    for i in range(0, len(cmp_df['frame']), qps)
                ], 
                [
                    temp[i]
                    for i in range(0, len(cmp_df['frame']), qps)
                ],
            ],
            names = self.__indexes__
        )
        return index