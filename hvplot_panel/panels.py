# -*- coding: utf-8 -*-

"""Main module."""

import datashader as ds
# import datetime as dt
import holoviews as hv
import panel as pn
import param
from datashader.colors import Sets1to3
from holoviews.operation.datashader import datashade

from .axis_options import AxisOptionsPanel


class LinePanel(param.Parameterized):
    """
    Default panel for hvplot `line tool https://hvplot.pyviz.org/user_guide/Plotting.html#The-plot-method`
    """
    x = param.ObjectSelector(default="yellow", objects=["red", "yellow", "green"])
    y = param.ListSelector(default=["yellow"], objects=["red", "yellow", "green"])

    #######################
    # Optional parameters #
    #######################
    options_axis = param.Parameter(precedence=3)
    datashade = param.Boolean(default=True, doc='Enable datashade possibilities')
    max_step = param.Integer(default=10000, bounds=(1, 100000))
    color_key = hv.Cycle(Sets1to3)
    gif = pn.pane.GIF('https://upload.wikimedia.org/wikipedia/commons/b/b1/Loading_icon.gif', aspect_ratio=1)

    def __init__(self, dataframe=None, objects=None, defaults=None, **params):
        """
            :param dataframe: Pandas dataframe formatted (e.g. all types are well defined,...)
            :param objects: Dictionary to populate param widget
            :param defaults: Dictionary to set the default value of widget
            :param params: all other params
         """
        if "options" not in params:
            params["options_axis"] = AxisOptionsPanel(name="Options", dataframe=dataframe, objects=objects,
                                                      defaults=defaults)
        self.dataframe = dataframe
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
            'x': self.x,
            'y': self.y,
            #######################
            # Generic opts param. #
            #######################
            'width': self.options_axis.width,
            'height': self.options_axis.height,
            'shared_axes': self.options_axis.shared_axes,
            'grid': self.options_axis.grid,
            'legend': self.options_axis.legend,
            'rot': self.options_axis.rot,
            # 'xlim'                   : self.options_axis.xlim,
            # 'ylim'                   : self.options_axis.ylim,
            #                 'xticks'                 : self.options_axis.xticks,
            #                 'yticks'                 : self.options_axis.yticks,
            'colorbar': self.options_axis.colorbar,
            'invert': self.options_axis.invert,
            'title': self.options_axis.title,
            'logx': self.options_axis.logx,
            'logy': self.options_axis.logy,
            'loglog': self.options_axis.loglog,
            'xaxis': self.options_axis.xaxis,
            'yaxis': self.options_axis.yaxis,
            # 'xformatter'             : self.options_axis.xformatter,
            # 'yformatter'             : self.options_axis.yformatter,
            'xlabel': self.options_axis.xlabel,
            'ylabel': self.options_axis.ylabel,
            # 'padding'                : self.options_axis.padding,
            'alpha': 1,
            'color': self.color_key
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
        """
        Use of datashade for performance and line for hover tool capabilities
        :return: Panel of this combination
        """
        # Select only sufficient data
        if self.x in self.y:
            self.y.remove(self.x)
        if self.y == []:
            return self.gif

        df = self.dataframe[[self.x] + self.y].copy()
        lines_overlay = df.hvplot(**self.plot_options).options({'Curve': {'color': self.color_key}})

        def hover_curve(x_range=[df.index.min(), df.index.max()]):  # , y_range):
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
                return plot_df.options({'Curve': {'color': self.color_key}})

        # Define a RangeXY stream linked to the image
        rangex = hv.streams.RangeX(source=lines_overlay)
        data_shade_plot = hv.DynamicMap(hover_curve, streams=[rangex])
        if len(self.y) == 1:
            data_shade_plot *= datashade(lines_overlay)
        else:
            data_shade_plot *= datashade(lines_overlay, aggregator=ds.count_cat('Variable'))
        return pn.panel(data_shade_plot)

    def panel(self):
        return pn.Row(self.param, self.view)


class BoxPanel(param.Parameterized):
    """
        Default panel for hvplot `box tool https://hvplot.pyviz.org/user_guide/Plotting.html#Area`
    """
    y = param.ObjectSelector(default="yellow", objects=["red", "yellow", "green"])
    by = param.ListSelector(default=["yellow"], objects=["red", "yellow", "green"])

    #######################
    # Optional parameters #
    #######################
    options_axis = param.Parameter(precedence=3)

    def __init__(self, dataframe=None, objects=None, defaults=None, **params):
        """
            :param dataframe: Pandas dataframe formatted (e.g. all types are well defined,...)
            :param objects: Dictionary to populate param widget
            :param defaults: Dictionary to set the default value of widget
            :param params: all other params
            """
        if "options" not in params:
            params["options_axis"] = AxisOptionsPanel(name="Options")
        self.dataframe = dataframe

        for k, v in objects.items():
            try:
                self.param[k].objects = v
            except Exception as e:
                print(e)
                pass
        for k, v in defaults.items():
            try:
                setattr(self, k, v)
            except Exception as e:
                print(e)
                pass
        super(BoxPanel, self).__init__(**params)

        self.set_options()

    def set_options(self):
        self.plot_options = {
            'y': self.y,
            'by': self.by,
            #######################
            # Generic opts param. #
            #######################
            'width': self.options_axis.width,
            'height': self.options_axis.height,
            'shared_axes': self.options_axis.shared_axes,
            'grid': self.options_axis.grid,
            'legend': self.options_axis.legend,
            'rot': self.options_axis.rot,
            # 'xlim'                           : self.options_axis.xlim,
            # 'ylim'                           : self.options_axis.ylim,
            # 'xticks'                         : self.options_axis.xticks,
            # 'yticks'                         : self.options_axis.yticks,
            'colorbar': self.options_axis.colorbar,
            'invert': self.options_axis.invert,
            'title': self.options_axis.title,
            # 'logx'                           : self.options_axis.logx,
            # 'logy'                           : self.options_axis.logy,
            # 'loglog'                         : self.options_axis.loglog,
            'xaxis': self.options_axis.xaxis,
            'yaxis': self.options_axis.yaxis,
            # 'xformatter'                     : self.options_axis.xformatter,
            # 'yformatter'                     : self.options_axis.yformatter,
            'xlabel': self.options_axis.xlabel,
            'ylabel': self.options_axis.ylabel,
            # 'padding'                        : self.options_axis.padding,
        }

    @param.depends(
        'y',
        'by',
        'options_axis.width',
        'options_axis.height',
        'options_axis.shared_axes',
        'options_axis.grid',
        'options_axis.legend',
        'options_axis.rot',
        #               'options_axis.xlim',
        #               'options_axis.ylim',
        'options_axis.xticks',
        'options_axis.yticks',
        'options_axis.colorbar',
        'options_axis.invert',
        'options_axis.title',
        #               'options_axis.logx',
        #               'options_axis.logy',
        #               'options_axis.loglog',
        'options_axis.xaxis',
        'options_axis.yaxis',
        #               'options_axis.xformatter',
        #               'options_axis.yformatter',
        'options_axis.xlabel',
        'options_axis.ylabel',
        #               'options_axis.padding',
        watch=True)
    def view(self):
        self.set_options()
        return self.dataframe.hvplot.box(**self.plot_options)

    def panel(self):
        return pn.Row(self.param, self.view)


class ScatterPanel(param.Parameterized):
    """
    Default panel for hvplot `scatter tool https://hvplot.pyviz.org/user_guide/Plotting.html#Scatter`
    """

    x = param.ObjectSelector(default="yellow", objects=["red", "yellow", "green"])
    y = param.ListSelector(default=["yellow"], objects=["red", "yellow", "green"])

    #######################
    # Optional parameters #
    #######################
    options_axis = param.Parameter(precedence=3)

    def __init__(self, dataframe=None, objects=None, defaults=None, **params):
        """
            :param dataframe: Pandas dataframe formatted (e.g. all types are well defined,...)
            :param objects: Dictionary to populate param widget
            :param defaults: Dictionary to set the default value of widget
            :param params: all other params
            """
        if "options" not in params:
            params["options_axis"] = AxisOptionsPanel(name="Options")
        self.dataframe = dataframe
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
        super(ScatterPanel, self).__init__(**params)

        self.set_options()

    def set_options(self):
        self.plot_options = {
            'x': self.x,
            'y': self.y,
            #######################
            # Generic opts param. #
            #######################
            'width': self.options_axis.width,
            'height': self.options_axis.height,
            'shared_axes': self.options_axis.shared_axes,
            'grid': self.options_axis.grid,
            'legend': self.options_axis.legend,
            'rot': self.options_axis.rot,
            # 'xlim'                   : self.options_axis.xlim,
            # 'ylim'                   : self.options_axis.ylim,
            # 'xticks'                 : self.options_axis.xticks,
            # 'yticks'                 : self.options_axis.yticks,
            'colorbar': self.options_axis.colorbar,
            'invert': self.options_axis.invert,
            'title': self.options_axis.title,
            'logx': self.options_axis.logx,
            'logy': self.options_axis.logy,
            'loglog': self.options_axis.loglog,
            'xaxis': self.options_axis.xaxis,
            'yaxis': self.options_axis.yaxis,
            # 'xformatter'             : self.options_axis.xformatter,
            # 'yformatter'             : self.options_axis.yformatter,
            'xlabel': self.options_axis.xlabel,
            'ylabel': self.options_axis.ylabel,
            # 'padding'                : self.options_axis.padding,
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
        watch=True)
    def view(self):
        self.set_options()
        return self.dataframe.hvplot.scatter(**self.plot_options)

    def panel(self):
        return pn.Row(self.param, self.view)


class HistPanel(param.Parameterized):
    """
        Default panel for hvplot `histogram tool https://hvplot.pyviz.org/user_guide/Plotting.html#Histogram`
    """
    y = param.ListSelector(default=["yellow"], objects=["red", "yellow", "green"])
    by = param.ObjectSelector(default="yellow", objects=["red", "yellow", "green"])

    #######################
    # Optional parameters #
    #######################
    options_axis = param.Parameter(precedence=3)

    def __init__(self, dataframe=None, objects=None, defaults=None, **params):
        """
            :param dataframe: Pandas dataframe formatted (e.g. all types are well defined,...)
            :param objects: Dictionary to populate param widget
            :param defaults: Dictionary to set the default value of widget
            :param params: all other params
            """
        if "options" not in params:
            params["options_axis"] = AxisOptionsPanel(name="Options")
        self.dataframe = dataframe
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
        super(HistPanel, self).__init__(**params)

        self.set_options()

    def set_options(self):
        self.plot_options = {
            'y': self.y,
            'by': self.by,
            #######################
            # Generic opts param. #
            #######################
            'width': self.options_axis.width,
            'height': self.options_axis.height,
            'shared_axes': self.options_axis.shared_axes,
            'grid': self.options_axis.grid,
            'legend': self.options_axis.legend,
            'rot': self.options_axis.rot,
            # 'xlim'                   : self.options_axis.xlim,
            # 'ylim'                   : self.options_axis.ylim,
            # 'xticks'                 : self.options_axis.xticks,
            # 'yticks'                 : self.options_axis.yticks,
            'colorbar': self.options_axis.colorbar,
            'invert': self.options_axis.invert,
            'title': self.options_axis.title,
            'logx': self.options_axis.logx,
            'logy': self.options_axis.logy,
            'loglog': self.options_axis.loglog,
            'xaxis': self.options_axis.xaxis,
            'yaxis': self.options_axis.yaxis,
            # 'xformatter'             : self.options_axis.xformatter,
            # 'yformatter'             : self.options_axis.yformatter,
            'xlabel': self.options_axis.xlabel,
            'ylabel': self.options_axis.ylabel,
            # 'padding'                : self.options_axis.padding,
        }

    @param.depends(
        'y',
        'by',
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
        watch=True)
    def view(self):
        self.set_options()
        return self.dataframe.hvplot.hist(**self.plot_options)

    def panel(self):
        return pn.Row(self.param, self.view)


# %load ../hvplot_panel/bar_panel.py
class BarPanel(param.Parameterized):
    """
        Default panel for hvplot `bar tool https://hvplot.pyviz.org/user_guide/Plotting.html#Bars`
    """

    x = param.ObjectSelector(default="yellow", objects=["red", "yellow", "green"])
    y = param.ListSelector(default=["yellow"], objects=["red", "yellow", "green"])
    stacked = param.Boolean(default=False)

    #######################
    # Optional parameters #
    #######################
    options_axis = param.Parameter(precedence=3)

    def __init__(self, dataframe=None, objects=None, defaults=None, **params):
        """
            :param dataframe: Pandas dataframe formatted (e.g. all types are well defined,...)
            :param objects: Dictionary to populate param widget
            :param defaults: Dictionary to set the default value of widget
            :param params: all other params
            """
        if "options" not in params:
            params["options_axis"] = AxisOptionsPanel(name="Options")
        self.dataframe = dataframe
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
        super(BarPanel, self).__init__(**params)

        self.set_options()

    def set_options(self):
        self.plot_options = {
            'x': self.x,
            'y': self.y,
            'stacked': self.stacked,
            #######################
            # Generic opts param. #
            #######################
            'width': self.options_axis.width,
            'height': self.options_axis.height,
            'shared_axes': self.options_axis.shared_axes,
            'grid': self.options_axis.grid,
            'legend': self.options_axis.legend,
            'rot': self.options_axis.rot,
            # 'xlim'                   : self.options_axis.xlim,
            # 'ylim'                   : self.options_axis.ylim,
            # 'xticks'                 : self.options_axis.xticks,
            # 'yticks'                 : self.options_axis.yticks,
            'colorbar': self.options_axis.colorbar,
            'invert': self.options_axis.invert,
            'title': self.options_axis.title,
            'logx': self.options_axis.logx,
            'logy': self.options_axis.logy,
            'loglog': self.options_axis.loglog,
            'xaxis': self.options_axis.xaxis,
            'yaxis': self.options_axis.yaxis,
            # 'xformatter'             : self.options_axis.xformatter,
            # 'yformatter'             : self.options_axis.yformatter,
            'xlabel': self.options_axis.xlabel,
            'ylabel': self.options_axis.ylabel,
            # 'padding'                : self.options_axis.padding,
        }
        if len(self.y) == 1:
            self.plot_options['y'] = self.y[0]

    @param.depends(
        'x',
        'y',
        'stacked',
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
        watch=True)
    def view(self):
        self.set_options()
        return self.dataframe.hvplot.bar(**self.plot_options)

    def panel(self):
        return pn.Row(self.param, self.view)


class AreaPanel(param.Parameterized):
    """
        Default panel for hvplot `area tool https://hvplot.pyviz.org/user_guide/Plotting.html#Area`
    """
    x = param.ObjectSelector(default="yellow", objects=["red", "yellow", "green"])
    y = param.ListSelector(default=["yellow"], objects=["red", "yellow", "green"])
    y2 = param.ObjectSelector(default="yellow", objects=["red", "yellow", "green"])
    stacked = param.Boolean(default=False)

    #######################
    # Optional parameters #
    #######################
    options_axis = param.Parameter(precedence=3)

    def __init__(self, dataframe=None, objects=None, defaults=None, **params):
        """
            :param dataframe: Pandas dataframe formatted (e.g. all types are well defined,...)
            :param objects: Dictionary to populate param widget
            :param defaults: Dictionary to set the default value of widget
            :param params: all other params
            """
        if "options" not in params:
            params["options_axis"] = AxisOptionsPanel(name="Options")
        self.dataframe = dataframe
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
        super(AreaPanel, self).__init__(**params)

        self.set_options()

    def set_options(self):
        self.plot_options = {
            'x': self.x,
            'y': self.y,
            'y2': self.y2,
            'stacked': self.stacked,
            #######################
            # Generic opts param. #
            #######################
            'width': self.options_axis.width,
            'height': self.options_axis.height,
            'shared_axes': self.options_axis.shared_axes,
            'grid': self.options_axis.grid,
            'legend': self.options_axis.legend,
            'rot': self.options_axis.rot,
            # 'xlim'                   : self.options_axis.xlim,
            # 'ylim'                   : self.options_axis.ylim,
            # 'xticks'                 : self.options_axis.xticks,
            # 'yticks'                 : self.options_axis.yticks,
            'colorbar': self.options_axis.colorbar,
            'invert': self.options_axis.invert,
            'title': self.options_axis.title,
            'logx': self.options_axis.logx,
            'logy': self.options_axis.logy,
            'loglog': self.options_axis.loglog,
            'xaxis': self.options_axis.xaxis,
            'yaxis': self.options_axis.yaxis,
            # 'xformatter'             : self.options_axis.xformatter,
            # 'yformatter'             : self.options_axis.yformatter,
            'xlabel': self.options_axis.xlabel,
            'ylabel': self.options_axis.ylabel,
            # 'padding'                : self.options_axis.padding,
        }

    @param.depends(
        'x',
        'y',
        'y2',
        'stacked',
        'options_axis.width',
        'options_axis.height',
        'options_axis.shared_axes',
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
        watch=True)
    def view(self):
        self.set_options()
        return self.dataframe.hvplot.area(**self.plot_options)

    def panel(self):
        return pn.Row(self.param, self.view)


class HeatmapPanel(param.Parameterized):
    """
        Default panel for hvplot `heatmap tool https://hvplot.pyviz.org/user_guide/Plotting.html#HeatMap`
    """
    x = param.ObjectSelector(default="yellow",
                             objects=["red", "yellow", "green"])
    y = param.ObjectSelector(default="yellow",
                             objects=["red", "yellow", "green"])
    C = param.ObjectSelector(default="yellow",
                             objects=["red", "yellow", "green"])
    colorbar = param.Boolean(default=False, doc="Enables colorbar")
    reduce_function = param.String(default='np.mean',
                                   doc='Add reduce function')
    gspec = pn.GridSpec(width=800, height=600, mode='override')
    #######################
    # Optional parameters #
    #######################
    options_axis = param.Parameter(precedence=3)

    gif_pane = pn.pane.GIF(
        'https://upload.wikimedia.org/wikipedia/commons/b/b1/Loading_icon.gif')

    def __init__(self, dataframe=None, objects=None, defaults=None, **params):
        """
            :param dataframe: Pandas dataframe formatted (e.g. all types are well defined,...)
            :param objects: Dictionary to populate param widget
            :param defaults: Dictionary to set the default value of widget
            :param params: all other params
            """
        if "options" not in params:
            params["options_axis"] = AxisOptionsPanel(name="Options")
        self.dataframe = dataframe
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
        super(HeatmapPanel, self).__init__(**params)

        self.set_options()

    def set_options(self):

        self.plot_options = {
            'x': self.x,
            'y': self.y,
            'C': self.C,
            'colorbar': self.colorbar,
            # 'reduce_function': red_func,
        }
        self.axis_options = {
            #######################
            # Generic opts param. #
            #######################
            'width': self.options_axis.width,
            'height': self.options_axis.height,
            'shared_axes': self.options_axis.shared_axes,
            'grid': self.options_axis.grid,
            'legend': self.options_axis.legend,
            'rot': self.options_axis.rot,
            # 'xlim'                   : self.options_axis.xlim,
            # 'ylim'                   : self.options_axis.ylim,
            # 'xticks'                 : self.options_axis.xticks,
            # 'yticks'                 : self.options_axis.yticks,
            'colorbar': self.options_axis.colorbar,
            'invert': self.options_axis.invert,
            'title': self.options_axis.title,
            'logx': self.options_axis.logx,
            'logy': self.options_axis.logy,
            'loglog': self.options_axis.loglog,
            'xaxis': self.options_axis.xaxis,
            'yaxis': self.options_axis.yaxis,
            # 'xformatter'             : self.options_axis.xformatter,
            # 'yformatter'             : self.options_axis.yformatter,
            'xlabel': self.options_axis.xlabel,
            'ylabel': self.options_axis.ylabel,
            # 'padding'                : self.options_axis.padding,
        }
        red_func = eval(self.reduce_function)
        if hasattr(red_func, '__call__'):
            self.plot_options['reduce_function'] = red_func

        self.gspec.width = self.options_axis.width
        self.gspec.height = self.options_axis.height

    @param.depends(
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
        watch=True)
    def set_plot_options(self):
        self.plot.opts(**self.axis_options)

    @param.depends('x', 'y', 'C', 'colorbar', 'reduce_function', watch=True)
    def view(self):
        self.set_options()
        self.gspec[0, 0] = self.gif_pane
        self.plot = self.dataframe.hvplot_panel.heatmap(**self.plot_options)
        self.gspec[0, 0] = self.plot
        self.set_plot_options()
        return self.gspec

    def panel(self):
        return pn.Row(self.param, self.view)
