'''
Created on May 28, 2014

@author: tpmaxwel
'''

import vtk, os, sys
import numpy as np
from ConfigurationFunctions import SIGNAL

PackagePath = os.path.dirname( __file__ )  
DataDir = os.path.join( PackagePath, 'data' )
ButtonDir = os.path.join( DataDir, 'buttons' )

class OriginPosition:
    Upper_Left = [ 0, 1 ] 
    Upper_Right = [ 1, 1 ]  
    Lower_Left = [ 0, 0 ]  
    Lower_Right = [ 1, 0 ] 
    
class Orientation:
    Horizontal = 0 
    Vertical = 1 
    
class Button:
    
    FuncToggleStateOn = 1
    FuncToggleStateOff = 2
        
    def __init__( self, iren, **args ):
        self.StateChangedSignal = SIGNAL('StateChanged')
        self.invokingEvent = False
        self.renderWindowInteractor = iren
        self.names = args.get( 'names', [] )
        self.state = args.get( 'state', 0 )
        self.toggle = args.get( 'toggle', False )
        self.numberOfStates = args.get( 'nstates', ( 2 if self.toggle else len( self.names ) ) )
        self.id = args.get( 'id', self.names[0] if self.numberOfStates else None )
        self.key = args.get( 'key', None )
        self.image_size = None
        self.button_files = [ ]
        self.functionKeys = { }
        self.createButtonRepresentation()
        self.buttonWidget = vtk.vtkButtonWidget()
        self.buttonWidget.SetInteractor(self.renderWindowInteractor)
        self.buttonWidget.SetRepresentation( self.buttonRepresentation )
        self.buttonWidget.AddObserver( 'StateChangedEvent', self.processStateChangeEvent )
        self.buttonRepresentation.Highlight( self.state )
        
    def getFunctionMapKey (self, key, ctrl ):
        return "c-%c" % key if ctrl else "%c" % key

    def addFunctionKey(self, key, ctrl, function ):
        fkey =  self.getFunctionMapKey( key, ctrl )       
        self.functionKeys[ fkey ]  = function
        
    def processFunctionKey( self, key, ctrl ):
        fkey =  self.getFunctionMapKey( key, ctrl )       
        function = self.functionKeys.get( fkey, None )
        if function <> None: 
            self.executeFunction( function )
            return 1
        return 0
    
    def executeFunction( self, function ):
        if   function == Button.FuncToggleStateOn:  self.setToggleState( 1 )
        elif function == Button.FuncToggleStateOff: self.setToggleState( 0 )
    
    def createButtonRepresentation(self, **args):
        JPEGReader = vtk.vtkJPEGReader()
        self.buttonRepresentation = vtk.vtkTexturedButtonRepresentation2D()
        self.buttonRepresentation.SetPlaceFactor( args.get( 'scale', 1 ) )
        num_images = len( self.names )
        if num_images:           
            self.buttonRepresentation.SetNumberOfStates(num_images)
            for button_index in range( num_images ):                
                buttonFilePath = os.path.join( ButtonDir,  '.'.join( [ self.names[ button_index ], 'jpeg' ] ) )
                JPEGReader.SetFileName ( buttonFilePath )
                JPEGReader.Update()
                image_data = JPEGReader.GetOutput()
                if self.image_size == None: self.image_size = image_data.GetDimensions()
                self.buttonRepresentation.SetButtonTexture( button_index, image_data )
                self.button_files.append( buttonFilePath )
            self.setToggleProps()
        
    def addObserver(self, observer, **args ):
        event = args.get( 'event', 'StateChangedEvent' )
        self.buttonWidget.AddObserver( event, observer )
        
    def setToggleProps(self, state = None ):
        if self.toggle:
            prop = self.buttonRepresentation.GetProperty()
            prop.SetOpacity( 0.4 if ( self.state == 0 ) else 1.0 )
            self.buttonRepresentation.SetProperty(prop)
            prop = self.buttonRepresentation.GetHoveringProperty()
            prop.SetOpacity( 0.7 if ( self.state == 0 ) else 1.0 )
            self.buttonRepresentation.SetHoveringProperty(prop)
            self.buttonRepresentation.Modified()
            self.buttonRepresentation.NeedToRenderOn()
            
    def processKeyEvent( self, key, ctrl = 0 ):
        if self.processFunctionKey( key, ctrl ): 
            return True        
        if key == self.key and not self.invokingEvent:
            self.buttonRepresentation.Highlight( self.buttonRepresentation.HighlightSelecting )
            self.processStateChangeEvent( self, "KeyEvent", True )
            self.buttonRepresentation.Highlight( self.buttonRepresentation.HighlightNormal )
            return True
        return False
    
    def setToggleState( self, state ):
        self.state = state
        self.setToggleProps()       

    def processStateChangeEvent( self, obj, event, indirect = False ):
        self.invokingEvent = True
        self.state = ( self.state + 1 ) % self.numberOfStates
        self.StateChangedSignal( self.id, self.key, self.state )
        if (self.key <> None) and not indirect:
            self.renderWindowInteractor.SetKeyEventInformation( 0, 0, self.key, 1, self.key )
            self.renderWindowInteractor.InvokeEvent( 'CharEvent' )
        self.setToggleProps()
        self.invokingEvent = False
            
        print " ** Process State Change Event: id = %s, state = %d " % ( self.id, self.state )
        
    def place( self, bounds ):
        self.buttonRepresentation.PlaceWidget( bounds )
        
    def size(self):
        return self.image_size
    
    def On(self):
        self.buttonWidget.On()

    def Off(self):
        self.buttonWidget.Off()
    
class ButtonBarWidget:
    
    def __init__( self, name, interactor, **args ):
        self.vtk_coord = vtk.vtkCoordinate()
        self.vtk_coord.SetCoordinateSystemToNormalizedDisplay()
        self.StateChangedSignal = SIGNAL('StateChanged')
        self.interactor = interactor
        self.name = name 
        self.origin = args.get( 'origin', OriginPosition.Upper_Left )
        self.orientation = args.get( 'orientation', Orientation.Vertical )
        self.position = args.get( 'position', ( 0.0, 1.0 ) )
        self.buffer = args.get( 'buffer', ( 3, 3 ) )
        self.windowSizeRange = [ 200, 1200 ]
        self.minScale = 0.3
        self.buttons = []
        self.visible = False
        self.updateWindowSize()
        
    def updateWindowSize(self):
        self.windowSize = self.interactor.GetRenderWindow().GetSize()
        
    def build( self, **args ):
        current_location = self.getScreenPosition( self.position )
        for button in self.buttons:
            current_location = self.placeButton( button, current_location )
            
    def reposition( self, **args ):
        print "Reposition: %d " % self.windowSize[0]
        self.updateWindowSize()
        self.build( **args )
             
    def placeButton( self, button, position, **args ):
        max_size = button.size()
        scale = 1.0 if self.windowSize[0] > self.windowSizeRange[1] else float(self.windowSize[0])/self.windowSizeRange[1]
        size = [ max_size[0]*scale, max_size[1]*scale ]
        bounds = self.computeBounds( position, size )
        print " placeButton[%s]: bounds = %s" % ( button.id, str(bounds) )
        button.place( bounds )
        return self.getOffsetScreenPosition( size, position )
        
    def addButton( self, **args ):
        button = Button( self.interactor, **args )
        button.StateChangedSignal.connect( self.processStateChangeEvent )
        self.buttons.append( button )
        return button
    
    def getScreenPosition(self, normalized_display_position, buffered = True ):
        self.vtk_coord.SetValue(  normalized_display_position[0], normalized_display_position[1] )
        screen_pos = self.vtk_coord.GetComputedDisplayValue( self.getRenderer() )
        if buffered: screen_pos = self.getBufferedPos( screen_pos  )
        return screen_pos
  
    def getBufferedPos( self, screen_pos ): 
        buff_screen_pos = list( screen_pos )         
        for ic in range(2):
            if self.origin[ic]:  buff_screen_pos[ic] = screen_pos[ic] - self.buffer[ic]
            else:                buff_screen_pos[ic] = screen_pos[ic] + self.buffer[ic]
        return buff_screen_pos
            
    def getOffsetScreenPosition( self, bsize, current_location ):
        offset_location = list( current_location )
        offset = [ bsize[0] + self.buffer[0], bsize[1] + self.buffer[1] ]
        if self.orientation == Orientation.Vertical:
            offset_location[1] = offset_location[1] - offset[1] if self.origin[1] else offset_location[1] + offset[1]
        if self.orientation == Orientation.Horizontal:
            offset_location[0] = offset_location[0] - offset[0] if self.origin[0] else offset_location[0] + offset[0]
        return offset_location
            
    def processStateChangeEvent( self, button_id, key, state ):
        self.StateChangedSignal( button_id, key, state )

    def computeBounds( self, pos, size ):
        bds = [0.0]*6
        bds[0] = pos[0] - size[0] if self.origin[0] else pos[0]
        bds[1] = pos[0] if self.origin[0] else pos[0] + size[0]
        bds[2] = pos[1] - size[1] if self.origin[1] else pos[1]
        bds[3] = pos[1] if self.origin[1] else pos[1] + size[1]
        return bds
    
    def show(self):
        print "Show button bar ", self.name
        self.visible = True
        for button in self.buttons: button.On()
        
    def processKeyEvent( self, key, ctrl = 0 ):
        processed = False
        for button in self.buttons: 
            if button.processKeyEvent( key, ctrl ): 
                processed = True
        return processed
 
    def hide(self):
        print "Hide button bar ", self.name
        self.visible = False
        for button in self.buttons: button.Off()
            
    def toggleVisibility(self):
        if self.visible: 
            self.hide()
        else:
            self.updatePositions() 
            self.show()
            
    def getRenderer(self):
        rw = self.interactor.GetRenderWindow()
        return rw.GetRenderers().GetFirstRenderer ()

if __name__ == '__main__':
        
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    iren.SetInteractorStyle( vtk.vtkInteractorStyleTrackballCamera() )
    ren.SetBackground( 1.0, 1.0, 1.0 )
    renWin.SetSize(1000,800)
    
    buttonBarWidget = ButtonBarWidget( "Test", iren, orientation=Orientation.Vertical )
    buttonBarWidget.addButton( names=['ScaleColormap'], id='Scale Colormap', key='S' )
    buttonBarWidget.addButton( names=['Configure'], id='Configure', key='C' )

    ren.ResetCamera()
    ren.ResetCameraClippingRange()   
    iren.Initialize()
    renWin.Render()
    
    buttonBarWidget.build()
    buttonBarWidget.show()
    
    iren.Start()