'''
Created on May 22, 2014

@author: tpmaxwel
'''
import vtk
import numpy as np
from ColorMapManager import *

def getScalars( image_data, x, y ):
    comp_data = [ int( image_data.GetScalarComponentAsFloat ( x, y, 0, ic ) ) for ic in range( 4 ) ]
    return str( comp_data )
        
class ListWidget:
    
    def __init__( self, interactor, **args ):
        self.buttonRepresentation = None
        self.interactor = interactor
        self.buttons = []
    
    def getButton( self, **args ):
        buttonRepresentation = self.getButtonRepresentation( **args )
        buttonRepresentation.SetPlaceFactor( args.get( 'scale', 1 ) )
        position = args.get( 'position', [ 1.0, 1.0 ] )
        size = args.get( 'size', [ 80.0, 40.0 ] )
        buttonRepresentation.PlaceWidget( self.computeBounds(position,size) )
        buttonWidget = vtk.vtkButtonWidget()
        buttonWidget.SetInteractor(self.interactor)
        buttonWidget.SetRepresentation(buttonRepresentation)
        self.buttons.append( buttonWidget )
        return buttonWidget
    
    def getButtonRepresentation(self):
        return None
    
    def show(self):
        for button in self.buttons:
            button.On()
            button.Render()
 
    def hide(self):
        for button in self.buttons:
            button.Off()
            
    def getRenderer(self):
        rw = self.interactor.GetRenderWindow()
        return rw.GetRenderers().GetFirstRenderer ()
            
    def computeBounds( self, normalized_display_position, size ):
        renderer = self.getRenderer()
        upperRight = vtk.vtkCoordinate()
        upperRight.SetCoordinateSystemToNormalizedDisplay()
        upperRight.SetValue( normalized_display_position[0], normalized_display_position[1] )
        bds = [0.0]*6
        bds[0] = upperRight.GetComputedDisplayValue(renderer)[0] - size[0]
        bds[1] = bds[0] + size[0]
        bds[2] = upperRight.GetComputedDisplayValue(renderer)[1] - size[1]
        bds[3] = bds[2] + size[1]
        return bds

# class TextListWidget(ListWidget):    
# 
#     def __init__( self, interactor, **args ):
#         ListWidget.__init__( self, interactor, **args )   
# 
#     def getButtonRepresentation(self, **args):
#         labels = args.get( 'labels', [] )
#         buttonRepresentation = vtk.vtkProp3DButtonRepresentation()
#         nstates = len( labels )
#         buttonRepresentation.SetNumberOfStates(nstates)
#         for button_index in range( nstates ):
#             text_actor = vtk.vtkTextActor()
#             text_actor.SetInput(labels[button_index])
#             text_actor.GetTextProperty().SetColor((1, 1, 1))
#             buttonRepresentation.SetButtonProp( button_index, text_actor )
#         return buttonRepresentation
               
class TexturedListWidget(ListWidget):    

    def __init__( self, interactor, **args ):
        ListWidget.__init__( self, interactor, **args )     
        self.lut = vtk.vtkLookupTable()
        self.colorMapManager = ColorMapManager( self.lut ) 
        self.textMapper = None
                 
    def getButtonRepresentation(self, **args):
        buttonRepresentation = vtk.vtkTexturedButtonRepresentation2D()
        images = args.get( 'images', None )
        if images:
            nstates = len( images )
            buttonRepresentation.SetNumberOfStates(nstates)
            for image_index in range( nstates ):
                image_data = self.getColorbarImage(  images[image_index] )
                buttonRepresentation.SetButtonTexture( image_index, image_data )
        labels = args.get( 'labels', None )
        if labels:
            if self.textMapper == None:
                size = args.get( 'size', [ 30.0, 30.0 ] )
                self.textRenderer = vtk.vtkFreeTypeUtilities()
            nstates = len( labels )
            buttonRepresentation.SetNumberOfStates(nstates)
            tprop = vtk.vtkTextProperty()
            for label_index in range( nstates ):
                texture = vtk.vtkImageData()
                self.textRenderer.RenderString( tprop, labels[label_index], 0, 0, texture ) 
                buttonRepresentation.SetButtonTexture( label_index, texture )
        return buttonRepresentation
    
    def getColorbarImage(self, cmap_name, **args ):
        cb_width = args.get( 'width', 100 )
        cmap_data = self.colorMapManager.load_array( cmap_name ) * 255.9 
        cmap_data = np.expand_dims( cmap_data[:,0:3].astype('uint8'), 0 )
        cmap_data = np.tile( cmap_data, ( cb_width, 1, 1 ) )       
        image = vtk.vtkImageData()
        image.SetDimensions(256,cb_width,1)
        if vtk.VTK_MAJOR_VERSION <= 5:  
            image.SetNumberOfScalarComponents(3)
            image.SetScalarTypeToUnsignedChar()
            image.AllocateScalars()
        else:
            image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,3)
        vtkdata =  image.GetPointData().GetScalars()
        vtkdata.SetVoidArray( cmap_data, cmap_data.size, 1 )
        return image
        
        
        
#         
#         
#         vtkdata = vtk.vtkUnsignedCharArray() 
#         nTup = cmap_data.size
#         vtkdata.SetNumberOfTuples( cb_width * 256 )
#         vtkdata.SetNumberOfComponents( 4 )
#         vtkdata.SetVoidArray( cmap_data, cmap_data.size, 1 )
#         vtkdata.SetName( "texture" )
#         vtkdata.Modified()
#         image = vtk.vtkImageData()
#         image.SetDimensions(256,10,1)
# #         if vtk.VTK_MAJOR_VERSION <= 5:  
# #             image.SetNumberOfScalarComponents(4)
# #             image.SetScalarTypeToUnsignedChar()
# #         else:
# #             image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,4)
#         pointData = image.GetPointData()
#         pointData.SetScalars( vtkdata )
#         return image
# 
#     def getColorbarImage1(self, cmap_name ):
#         image = vtk.vtkImageData()
#         image.SetDimensions(256,10,1)
#         if vtk.VTK_MAJOR_VERSION <= 5:  
#             image.SetNumberOfScalarComponents(3)
#             image.SetScalarTypeToUnsignedChar()
#             image.AllocateScalars()
#         else:
#             image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,3)
#         vtkdata =  image.GetPointData().GetScalars()
#         ntup = vtkdata.GetNumberOfTuples()
#         nc = vtkdata.GetNumberOfComponents()
# 
#         cmap_data = self.colorMapManager.load_array( cmap_name ) * 255.9 
#         for ic in range(3):
#             cmap_comp = cmap_data[:,ic].astype('uint8')
#             cmap_comp = np.expand_dims( cmap_comp, 1 )
#             cmap_comp = np.tile( cmap_comp, ( 1, 10 ) )
#             nTup = cmap_comp.size
#             vtkdata.SetVoidArray( cmap_comp, cmap_comp.size, 1 )
#             vtkdata.Modified()
#             internal_scalars = scalars.GetArray( ic )
#             internal_scalars.DeepCopy( vtkdata )
#         return image

    
if __name__ == '__main__':     
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.1, 0.2, 0.4)
     
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize( 1200, 800 )
     
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    interactor.Initialize()
    render_window.Render()
    
    list_widget = TexturedListWidget( interactor )
    list_widget.getButton( images=[ 'jet' ] )
#    list_widget.getButton( labels=[ 'test', 'ok' ] )
    list_widget.show()
         
    render_window.Render()
    interactor.Start()