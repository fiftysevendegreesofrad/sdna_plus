import arcpy
from arcpy import env
import math

'''handy utils for arcpy'''

def get_tolerance(in_polyline_feature_class):
    if env.XYTolerance != None:
        tolerance = env.XYTolerance
        arcpy.AddMessage("Using XYTolerance specified in environment: %f"%tolerance)
        return tolerance
    else:
       try:
            tolerance = arcpy.Describe(in_polyline_feature_class).spatialReference.XYTolerance
            arcpy.AddMessage("Using XYTolerance of input feature class: %f"%tolerance)
            return tolerance
       except:
            arcpy.AddError("Unable to obtain XYTolerance for near miss connection check")
            arcpy.AddError("  Either add a spatial reference to the feature class,")
            arcpy.AddError("  or override XYTolerance in the script environment settings.")
            raise 

def get_z_tolerance(in_polyline_feature_class):
    if env.ZTolerance != None:
        tolerance = env.ZTolerance
        arcpy.AddMessage("Using ZTolerance specified in environment: %f"%tolerance)
        return tolerance
    else:
       try:
            tolerance = arcpy.Describe(in_polyline_feature_class).spatialReference.ZTolerance
            if not math.isnan(tolerance):
                arcpy.AddMessage("Using ZTolerance of input feature class: %f"%tolerance)
                return tolerance
            else:
                arcpy.AddMessage("Input feature class has spatial reference but no z tolerance")
                arcpy.AddMessage("Using z tolerance of 0")
                return 0
       except:
            arcpy.AddError("Unable to obtain ZTolerance for near miss connection check")
            arcpy.AddError("  Either add a spatial reference to the feature class,")
            arcpy.AddError("  or override ZTolerance in the script environment settings.")
            raise 

def clear_selection(layer):
    arcpy.SelectLayerByAttribute_management(layer, "CLEAR_SELECTION")

def select_edges(layer,in_arc_idfield,edge_list):
    # build where clause
    sql_clause = ' OR '.join(['"%s"=%s'%(in_arc_idfield,str(link)) for link in edge_list])
    arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", sql_clause)
    arcpy.RefreshActiveView()
