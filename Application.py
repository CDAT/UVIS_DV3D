'''
Created on May 13, 2014

@author: tpmaxwel
'''
import cdms2
from PointCloudViewer import CPCPlot
#from VolumeViewer import VolumePlot
from SliceViewer import SlicePlot
from RectilinearGridPlot import RectGridPlot
from ConfigurationFunctions import PlotType

class DV3D:
    
    def __init__( self, **args ):
        self.use_gui = args.get( 'gui', False )
        if self.use_gui: self.initGui()
        
    def initGui(self):
        pass
    
    def init(self, **args ):
        
        init_args = args[ 'init' ]
        ( grid_file, data_file, interface, varname, grd_coords, var_proc_op, ROI, subSpace ) = init_args
        df = cdms2.open( data_file )       
        var = df[ varname ]
        grid_metadata = var.getGrid()

        plot_type = PlotType.getPointsLayout( grid_metadata )
        
        if plot_type == PlotType.Grid:
            g = RectGridPlot(gui=self.use_gui) 
#            g = SlicePlot(gui=self.use_gui)            
#            g = VolumePlot(gui=self.use_gui) 
            g.init( **args ) 
        else:
            g = CPCPlot(gui=self.use_gui) 
            g.init( **args  )                  
        
