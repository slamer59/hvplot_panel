import param


class AxisOptionsPanel(param.Parameterized):
    """
    Class (try) to define all axis options available for Panel
    """

    width = param.Integer(default=800, bounds=(200, 1600))
    height = param.Integer(default=600, bounds=(200, 1600))
    shared_axes = param.Boolean(True, doc="Share axes parameter")
    grid = param.Boolean(default=False, doc="Whether to show a grid")
    legend = param.ObjectSelector(default="top", objects=("top_right", "top_left", "bottom_left", "bottom_right", "right", "left", "top", "bottom", None), 
                                  doc="Whether to show a legend, or a legend position")
    rot = param.Integer(default=45, bounds=(0, 180),
                        doc="Rotates the axis ticks along the x-axis by the specified number of degrees.")
    #        xlim        = param.Number(8.2,bounds=(7.5,10))
    #        ylim        = param.Number(8.2,bounds=(7.5,10))
    xticks = param.Integer(default=6, bounds=(1, 10))
    yticks = param.Integer(default=6, bounds=(1, 10))
    colorbar = param.Boolean(default=False, doc="Enables colorbar")
    invert = param.Boolean(default=False, doc="Swaps, x- y- Axis")
    title = param.String(default="")
    logx = param.Boolean(default=False, doc="Enables logarithmic x-axis")
    logy = param.Boolean(default=False, doc=" Enables logarithmic y-axis")
    loglog = param.Boolean(default=False, doc="Enables logarithmic x- and y-axis")
    xaxis = param.ObjectSelector(default="bottom", objects=["top", "bottom", None])
    yaxis = param.ObjectSelector(default="left", objects=["left", "right", None])
    #        xformatter  = param.String(default="%3.f")
    #        yformatter  = param.String(default="%3.f")
    xlabel = param.String(default="", doc="Axis labels for the x-axis")
    ylabel = param.String(default="", doc="Axis labels for the y-axis")

    #######################
    # Optional parameters #
    #######################
    #        options = param.Parameter(precedence=3)

    def __init__(self, dataframe=None, objects=None, defaults=None, **params):
        """
            :param dataframe: Pandas dataframe formatted (e.g. all types are well defined,...)
            :param objects: Dictionary to populate param widget
            :param defaults: Dictionary to set the default value of widget
            :param params: all other params
            """
        try:
            self.dataframe = dataframe
        except Exception as e:
            print(e)
        self.set_options()

        super(AxisOptionsPanel, self).__init__(**params)

    def set_options(self):
        self.plot_options = {
            'width': self.width,
            'height': self.height,
            'shared_axes': self.shared_axes,
            'grid': self.grid,
            'legend': self.legend,
            'rot': self.rot,
            #                'xlim'       : self.xlim,
            #                'ylim'       : self.ylim,
            'xticks': self.xticks,
            'yticks': self.yticks,
            'colorbar': self.colorbar,
            'invert': self.invert,
            'title': self.title,
            'logx': self.logx,
            'logy': self.logy,
            'loglog': self.loglog,
            'xaxis': self.xaxis,
            'yaxis': self.yaxis,
            #                'xformatter' : self.xformatter,
            #                'yformatter' : self.yformatter,
            'xlabel': self.xlabel,
            'ylabel': self.ylabel,
            #                'padding'    : self.padding,
        }

    def view(self):
        self.set_options()
        return self.plot_options
