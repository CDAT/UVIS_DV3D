'''
Created on May 28, 2014

@author: tpmaxwel
'''

import vtk, os
import numpy as np
from ConfigurationFunctions import SIGNAL

class OriginPosition:
    Upper_Left = [ 0, 1 ] 
    Upper_Right = [ 1, 1 ]  
    Lower_Left = [ 0, 0 ]  
    Lower_Right = [ 1, 0 ]  
    
class ButtonBarWidget:
    
    def __init__( self, interactor, **args ):
        self.StateChangedSignal = SIGNAL('StateChanged')
        self.interactor = interactor
        self.origin = args.get( 'origin', OriginPosition.Upper_Left )
        self.buttons = {}
        self.visible = False
        self.windowSize = self.interactor.GetRenderWindow().GetSize()
        
    def getButtonRepresentation(self, **args):
        buttonRepresentation = vtk.vtkTexturedButtonRepresentation2D()
        button_names = args.get( 'names', [] )
        numberOfStates = len( button_names )
        button_id = None
        image_size = None
        if numberOfStates:
            packagePath = os.path.dirname( __file__ )  
            dataDir = os.path.join( packagePath, 'data' )
            buttonDir = os.path.join( dataDir, 'buttons' )
            jPEGReader = vtk.vtkJPEGReader()
            button_id = args.get( 'id', button_names[0] )
            buttonRepresentation.SetNumberOfStates(numberOfStates)
            for button_index in range( numberOfStates ):                
                buttonFilePath = os.path.join( buttonDir,  '.'.join( [ button_names[ button_index ], 'jpeg' ] ) )
                jPEGReader.SetFileName ( buttonFilePath )
                jPEGReader.Update()
                image_data = jPEGReader.GetOutput()
                if image_size == None: image_size = image_data.GetDimensions()
                buttonRepresentation.SetButtonTexture( button_index, image_data )
        return button_id, image_size, buttonRepresentation
        
    def getButton( self, **args ):
        button_id, image_size, buttonRepresentation = self.getButtonRepresentation( **args )
        buttonRepresentation.SetPlaceFactor( args.get( 'scale', 1 ) )
        position = args.get( 'position', [ 0.0, 1.0 ] )
        size = args.get( 'size', image_size ) # [ 220.0, 35.0 ] )
        origin = args.get( 'origin', OriginPosition.Upper_Left )
        bounds = self.computeBounds( position, size, origin )
        print "Bounds = ", str( bounds )
        buttonRepresentation.PlaceWidget( bounds )
        buttonWidget = vtk.vtkButtonWidget()
        buttonWidget.SetInteractor(self.renderWindowInteractor)
        buttonWidget.SetRepresentation(buttonRepresentation)
        buttonWidget.AddObserver( 'StateChangedEvent', self.processStateChangeEvent )
        self.buttons[ buttonWidget ] = [ button_id, position, size ]
        return buttonWidget 
           
    def processStateChangeEvent( self, button, event ):
        button_rep = button.GetSliderRepresentation()
        state = button_rep.GetState()
        button_specs = self.buttons[ button ]
        button_id = button_specs[ 0 ]
        print " process State Change Event: ", button_id

    def computeBounds( self, normalized_display_position, size, origin=OriginPosition.Upper_Left, border = 2 ):
        renderer = self.getRenderer()
        upperRight = vtk.vtkCoordinate()
        upperRight.SetCoordinateSystemToNormalizedDisplay()
        upperRight.SetValue( normalized_display_position[0], normalized_display_position[1] )
        bds = [0.0]*6
        pos = upperRight.GetComputedDisplayValue(renderer)
        bds[0] = pos[0] - size[0] if origin[0] else pos[0]
        bds[1] = pos[0] if origin[0] else pos[0] + size[0]
        bds[2] = pos[1] - size[1] if origin[1] else pos[1]
        bds[3] = pos[1] if origin[1] else pos[1] + size[1]
        return bds
    
    def show(self):
        self.visible = True
        for button in self.buttons.keys():
            button.On()
#            button.Render()
 
    def hide(self):
        self.visible = False
        for button in self.buttons.keys():
            button.Off()
            
    def toggleVisibility(self):
        if self.visible: 
            self.hide()
        else:
            self.updatePositions() 
            self.show()
            
    def getRenderer(self):
        rw = self.interactor.GetRenderWindow()
        return rw.GetRenderers().GetFirstRenderer ()
    
