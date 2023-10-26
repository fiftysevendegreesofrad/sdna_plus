import arcpy
from arcpy import env
import os

def add_field_to_table(table,idfield,name,datatype,arcid_to_data_function):
    arcpy.AddMessage('adding field')
    arcpy.AddField_management(table,name,datatype)
    arcpy.AddMessage('added field... populating now...')

    rows = arcpy.UpdateCursor(table)
    for row in rows:
        row.setValue(name,arcid_to_data_function(row.getValue(idfield)))
        rows.updateRow(row) 
    del row
    del rows
    arcpy.AddMessage('...done')

def add_multiple_fields_to_table(table,idfield,names,alii,datatype,arcid_to_data_function):
    names = [arcpy.ValidateFieldName(x,os.path.dirname(table)) for x in names]
    arcpy.AddMessage('adding fields: '+','.join(names))
    for name,alias in zip(names,alii):
        if name not in [x.name for x in arcpy.ListFields(table)]:
            arcpy.AddField_management(table,name,datatype,field_alias=alias)
        else:
            arcpy.AddWarning('field %s exists already, overwriting'%name)
    arcpy.AddMessage('added fields... populating now...')

    rows = arcpy.UpdateCursor(table)
    for row in rows:
        values = arcid_to_data_function(row.getValue(idfield))
        for i,name in enumerate(names):
            row.setValue(name,values[i])
        rows.updateRow(row) 
    del row
    del rows
    arcpy.AddMessage('...done')
