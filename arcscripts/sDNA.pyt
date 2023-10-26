import arcpy
import sdna_environment
import sDNAUISpec
import imp
imp.reload(sDNAUISpec)
from sDNAUISpec import get_tools
import runsdnacommand
imp.reload (runsdnacommand)
from runsdnacommand import runsdnacommand
import os,sys

def GetArcPythonExe():
    for p in sys.path:
        f = p+os.sep+"python.exe"
        if os.path.isfile(f):
            return f
    return None

# creates arcpy tools from sDNAUISpec 

def sDNA_type_to_arc_direction(datatype):
    return "Output" if datatype in ["OFC","OutFile"] else "Input"

sDNA_to_arc_type = {"FC":"GPFeatureLayer",
                    "OFC":"DEFeatureClass",
                    "Field":"Field",
                    "Text":"GPString",
                    "Bool":"GPBoolean",
                    "InFile":"File",
                    "OutFile":"File"}

sDNA_to_arc_fieldtype = {"Numeric":["Short","Long","Float","Double","OID"],"String":["Text"]}

tool_list = []

for tool in get_tools():

    class Tool(object):
        sdnatool = tool()
        label = tool.alias
        description = "<html>"+tool.desc+"</html>"
        category = tool.category
        canRunInBackground = True

        def getParameterInfo(self):
            params = []
            for varname,displayname,datatype,filter,default,required in self.sdnatool.getInputSpec():
                multivalue=False
                if datatype=="MultiField":
                    multivalue=True
                    datatype="Field"
                elif datatype=="MultiInFile":
                    multivalue=True
                    datatype="InFile"
                p = arcpy.Parameter(
                    displayName=displayname,
                    name=varname,
                    datatype=sDNA_to_arc_type[datatype],
                    parameterType="Required" if required else "Optional",
                    direction=sDNA_type_to_arc_direction(datatype),
                    multiValue=multivalue
                    )
                p.value = default
                params += [p]
                if filter:
                    if datatype=="Text":
                        p.filter.type = "ValueList"
                        p.filter.list = filter
                    if datatype=="FC":
                        p.filter.list = [filter]
                    if datatype=="Field":
                        allowabletypes,source = filter
                        p.filter.list = sDNA_to_arc_fieldtype[allowabletypes]
                        p.parameterDependencies = [source]
                    # Don't filter file types; ArcGIS bug means they only work on input files not output
            return params

        def isLicensed(self):
            return True

        def updateParameters(self, parameters):
            return

        def updateMessages(self, parameters):
            return

        def execute(self, parameters, messages):
            
            # join parameters to sDNAUISpec variable names
            varnames = [params[0] for params in self.sdnatool.getInputSpec()]
            args = dict(list(zip(varnames, [(p.ValueAsText if p.ValueAsText else "") for p in parameters])))
            
            # convert booleans from strings to bool
            booleanlist = [paramname for paramname,_,paramtype,_,_,_ in self.sdnatool.getInputSpec() if paramtype=="Bool"]
            for pn in booleanlist:
                args[pn]=(args[pn]==u"true")
                
            # get syntax to call tool
            syntax = self.sdnatool.getSyntax(args)
            
            # call by fork/exec to scripts in sDNA bin folder
            # convert input paths first
            newinputs = {}
            for name,layer in list(syntax["inputs"].items()):
                multis = layer.split(",")
                newmultilist=[]
                for m in multis:
                    m = m.strip()
                    if m:
                        newmultilist += [arcpy.Describe(m).catalogPath]
                newinputs[name]=",".join(newmultilist)
            syntax["inputs"]=newinputs                    
            
            # then call tool
            class ArcProgressorFacade:
                def __init__(self,arcgismessages,arcpy):
                    self.arcgismessages = arcgismessages
                    self.arcpy = arcpy
                    arcpy.SetProgressor("step", "", 0, 100, 1)
                def setInfo(self,info):
                    # split long lines or ArcGIS truncates them
                    maxchars = 200
                    lines = [info[i:i+maxchars] for i in range(0, len(info), maxchars)]
                    for line in lines:
                        self.arcgismessages.addMessage(line)
                def setPercentage(self,percent):
                    self.arcpy.SetProgressorPosition(int(percent))
            sdnapath = os.path.dirname(os.path.abspath(__file__))+os.sep+"bin"+os.sep
            pythonpath = str(";".join(sys.path))
            pythonexe = GetArcPythonExe()
            retcode = runsdnacommand(syntax,sdnapath,ArcProgressorFacade(messages,arcpy),pythonexe,pythonpath)
            if retcode!=0:
                messages.addErrorMessage("Process did not complete successfully")
            

    # rename class: have to play with locals() to fool arcgis I think
    newname = tool.__name__            
    Tool.__name__ = newname
    locals()[newname] = Tool
    del Tool
    tool_list += [locals()[newname]]
    
class Toolbox(object):
    def __init__(self):
        self.label = "Spatial Design Network Analysis"
        self.alias = "Spatial Design Network Analysis"
        self.tools = tool_list
