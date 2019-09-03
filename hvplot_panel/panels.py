# -*- coding: utf-8 -*-

"""Main module."""
import numpy as np
import pandas as pd
import hvplot.pandas
import panel as pn
import param
# import datetime as dt
import holoviews as hv
# import requests
# import dateutil.parser
import inspect
from datashader.colors import Sets1to3
from holoviews.operation.datashader import datashade
import datashader as ds
# import intake

from axis_options import AxisOptionsPanel

class LinePanel(param.Parameterized):

        x = param.ObjectSelector(default="yellow", objects=["red","yellow","green"])
        y = param.ListSelector(default=["yellow"], objects=["red","yellow","green"])

        #######################
        # Optional parameters #
        #######################
        options_axis = param.Parameter(precedence=3)
        datashade    = param.Boolean(default=True, doc='Enable datashade possibilities')
        max_step     = param.Integer(default=10000, bounds=(1, 100000))
        color_key    = hv.Cycle(Sets1to3)
        gif          = pn.pane.GIF('https://upload.wikimedia.org/wikipedia/commons/b/b1/Loading_icon.gif', aspect_ratio=1)

        def __init__(self, dataframe=None, objects=None, defaults=None, **params):
            if "options" not in params:
                params["options_axis"] = AxisOptionsPanel(name="Options", dataframe=dataframe, objects=objects, defaults=defaults)
            if dataframe is not None:
                self.dataframe = dataframe
            else:
                self.dataframe = df
            for k, v in objects.items():
                try:
                    self.param[k].objects = v
                except:
                    pass
            for k, v in defaults.items():
                try:
                    setattr(self, k, v)
                except:
                    pass
            super(LinePanel, self).__init__(**params)

            self.set_options()

        def set_options(self):
            self.plot_options = {
                'x' : self.x,
                'y' : self.y,
        #######################
        # Generic opts param. #
        #######################
                 'width'                  : self.options_axis.width,
                 'height'                 : self.options_axis.height,
                 'shared_axes'            : self.options_axis.shared_axes,
                 'grid'                   : self.options_axis.grid,
                 'legend'                 : self.options_axis.legend,
                 'rot'                    : self.options_axis.rot,
                # 'xlim'                   : self.options_axis.xlim,
                # 'ylim'                   : self.options_axis.ylim,
#                 'xticks'                 : self.options_axis.xticks,
#                 'yticks'                 : self.options_axis.yticks,
                 'colorbar'               : self.options_axis.colorbar,
                 'invert'                 : self.options_axis.invert,
                 'title'                  : self.options_axis.title,
                 'logx'                   : self.options_axis.logx,
                 'logy'                   : self.options_axis.logy,
                 'loglog'                 : self.options_axis.loglog,
                 'xaxis'                  : self.options_axis.xaxis,
                 'yaxis'                  : self.options_axis.yaxis,
                # 'xformatter'             : self.options_axis.xformatter,
                # 'yformatter'             : self.options_axis.yformatter,
                 'xlabel'                 : self.options_axis.xlabel,
                 'ylabel'                 : self.options_axis.ylabel,
                # 'padding'                : self.options_axis.padding,
                 'alpha':               1,
                 'color'                   : self.color_key
            }

        @param.depends(
               'x',
               'y',
               'options_axis.width',
               'options_axis.height',
               'options_axis.shared_axes',
               'options_axis.grid',
               'options_axis.legend',
               'options_axis.rot',
#               'options_axis.xlim',
#               'options_axis.ylim',
#               'options_axis.xticks',
#               'options_axis.yticks',
               'options_axis.colorbar',
               'options_axis.invert',
               'options_axis.title',
               'options_axis.logx',
               'options_axis.logy',
               'options_axis.loglog',
               'options_axis.xaxis',
               'options_axis.yaxis',
#               'options_axis.xformatter',
#               'options_axis.yformatter',
               'options_axis.xlabel',
               'options_axis.ylabel',
#               'options_axis.padding',
                'datashade',
                'max_step',
             watch=True)
        def view(self):
            self.set_options()
            if self.datashade:
                return self.view_datashade()
            else:
                return self.dataframe.hvplot.line(**self.plot_options)
        
        def view_datashade(self):
            # Select only sufficient data
            if self.x in self.y:
                self.y.remove(self.x)
            if self.y == []:
                return self.gif
            
            df = self.dataframe[[self.x]+self.y].copy()
            # def datashade_plot():
            from datashader.colors import Sets1to3


            color_key = hv.Cycle(Sets1to3)
            lines_overlay = df.hvplot(**self.plot_options).options({'Curve': {'color': color_key}})
            def hover_curve(x_range=[df.index.min(),df.index.max()]): #, y_range):
                # Compute
                dataframe = df.copy()
                if x_range is not None:
                    dataframe = dataframe[(dataframe.index > x_range[0]) & (dataframe.index < x_range[1])]
                data_length = len(dataframe) * len(dataframe.columns)
                step = 1 if data_length < self.max_step else data_length // self.max_step
                plot_df = dataframe[::step].hvplot(**self.plot_options)
                if len(self.y) == 1:
                    return plot_df.options({'Curve': {'color': '#377eb8'}}) 
                else:
                    return plot_df.options({'Curve': {'color': color_key}}) 

            # Define a RangeXY stream linked to the image 
            rangex = hv.streams.RangeX(source=lines_overlay)
            data_shade_plot = hv.DynamicMap(hover_curve, streams=[rangex])
            if len(self.y) == 1:
                data_shade_plot *= datashade(lines_overlay)
            else:
                data_shade_plot *= datashade(lines_overlay, aggregator=ds.count_cat('Variable')) 

            self.data_shade_plot = pn.panel(data_shade_plot)
            return pn.panel(self.data_shade_plot)
        
        
        def panel(self):
            return pn.Row(self.param, self.view)
