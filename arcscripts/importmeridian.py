import arcpy,os
from arcpy import env
from collections import defaultdict

def point_dist(a,b):
        ax,ay = a
        bx,by = b
        return (bx-ax)**2 + (by-ay)**2

class Net:
        class Link:
                def __init__(self,points,linkid):
                        self.points = points
                        self.startelev = None
                        self.endelev = None
                        self.startelevcount = 0
                        self.endelevcount = 0
                        self.linkid = linkid
                def get_end_point(self,terminal):
                        assert(terminal=="1" or terminal=="2")
                        if terminal=="1":
                                return self.points[0]
                        else:
                                return self.points[-1]
                def set_elev(self,terminal,value):
                        assert(terminal=="1" or terminal=="2")
                        if terminal=="1":
                                self.startelev = value
                                self.startelevcount += 1
                        else:
                                self.endelev = value
                                self.endelevcount += 1
                def __repr__(self):
                        return "%s-%d%d"%(self.linkid,self.startelevcount,self.endelevcount)

        class Node:
                def __init__(self,point,nodeid,linkid,level,terminal):
                        self.point = point
                        self.nodeid = nodeid
                        self.linkid = linkid
                        self.level = level
                        self.terminal = terminal

        class ProblemNode:
                def __init__(self,node,problem):
                        self.node = node
                        self.problem = problem

        def __init__(self):
                self.links = defaultdict(list)
                self.nodes_from_point = defaultdict(list)
                self.nodes_from_id = defaultdict(list)
                self.problem_nodes = []

        def add_bare_link(self,points,linkid):
                link = self.Link(points,linkid)
                self.links[linkid].append(link)

        def add_node(self,point,nodeid,linkid,level,terminal):
                if not (terminal=="1" or terminal=="2"):
                        arcpy.AddMessage("Terminal other than 1 or 2")
                        assert(False)
                n = self.Node(point,nodeid,linkid,level,terminal)
                self.nodes_from_point[point].append(n)
                self.nodes_from_id[nodeid].append(n)

        def add_problem(self,node,problem):
                p = self.ProblemNode(node,problem)
                self.problem_nodes.append(p)

        def get_problems(self):
                for pn in self.problem_nodes:
                        yield pn.node.point,pn.problem

        def build(self):
                # assert all points have consistent nodeid
                arcpy.AddMessage("Checking all points have same nodeid")
                for nodelist in self.nodes_from_point.itervalues():
                        for node in nodelist[1:]:
                                if node.nodeid != nodelist[0].nodeid:
                                        self.add_problem(node,"Multiple node ids as single point")
                                        break

                # assert all nodeids have consistent point
                arcpy.AddMessage("Checking all nodeids have same point")
                for nodelist in self.nodes_from_id.itervalues():
                        for node in nodelist[1:]:
                                if node.nodeid != nodelist[0].nodeid:
                                        self.add_problem(node,"Multiple points for single node id")
                                        break

                # process nodes
                arcpy.AddMessage("Assigning elevations to links")
                for nodelist in self.nodes_from_id.itervalues():
                        # if there are duplicate linkid/terminal combinations ensure they have same level
                        nodes_this_point = defaultdict(list)
                        for node in nodelist:
                                nodes_this_point[(node.linkid,node.terminal)].append(node)
                        for supposedly_unique_node_list in nodes_this_point.values():
                                problem = False
                                for node in supposedly_unique_node_list[1:]:
                                        if node.level != supposedly_unique_node_list[0].level:
                                                problem = True
                                                break

                                node = supposedly_unique_node_list[0]
                                if problem:
                                        self.add_problem(node,"Multiple elevations specified for same link at same point")
                                else:
                                        self.process_node(node,len(supposedly_unique_node_list))

                # process links with no or multiple elevation
                arcpy.AddMessage("Finding links with no elevation")
                nodes_with_no_elevation = defaultdict(list)
                for link in self.get_edges():
                        if link.startelevcount == 0:
                                nodes_with_no_elevation[link.get_end_point("1")].append((link,"1"))
                        if link.endelevcount == 0:
                                nodes_with_no_elevation[link.get_end_point("2")].append((link,"2"))
                        if link.startelevcount > 1:
                                self.add_problem(self.Node(link.get_end_point("1"),None,None,None,None),"Elevation set multiple times (start)")
                        if link.endelevcount > 1:
                                self.add_problem(self.Node(link.get_end_point("2"),None,None,None,None),"Elevation set multiple times (end)")

                arcpy.AddMessage("Processing links with no elevation")
                for point,links in nodes_with_no_elevation.iteritems():
                        # if only two links with same id at this point, auto join though note problem
                        # if more links, note problem also
                        n = self.Node(point,None,None,None,None)
                        
                        if len(links)==2 and not point in self.nodes_from_point:
                                (link1,end1),(link2,end2) = links
                                if link1.linkid==link2.linkid:
                                        self.add_problem(n,"Auto joined split link")
                                else:
                                        self.add_problem(n,"Looks like split link but linkids don't match")
                        else:
                                if point in self.nodes_from_point:
                                        self.add_problem(n,"Node doesn't specify elevation for all links")
                                else:
                                        self.add_problem(n,"Multiple intersecting links without matching node")

                        # set all unknowns to 0
                        for link,end in links:
                                link.set_elev(end,0)

        def process_node(self,node,num_instances):
                # amazingly, linkid is not unique
                # so search for link end that's closest to node point and also matches linkid and terminal
                # then set elevation
                # if there are many equal closest, set all though assert the count matched the number of instances
                # if there are none, ignore though note the error
                closest_distance = float("inf")
                closest_links = []
                for link in self.links[node.linkid]:
                        link_end_point = link.get_end_point(node.terminal)
                        dist = point_dist(node.point,link_end_point)
                        if dist < closest_distance:
                                closest_distance = dist
                                closest_links = []
                        if dist == closest_distance:
                                closest_links.append(link)

                if len(closest_links) == 0:
                        self.add_problem(node,"No link matched to node")
                        return
                
                if closest_distance > 1:
                        self.add_problem(node,"Node is nowhere near corresponding link endpoint")
                        return

                if len(closest_links) != num_instances:
                        self.add_problem(node,"Mismatch between number of nodes and links with matching id")

                for link in closest_links:
                        link.set_elev(node.terminal,node.level)


        def get_edges(self):
                for x in self.links.values():
                        for y in x:
                                yield y

def read_feature_class(fcname,wanted_fields):
        arcpy.AddMessage("Reading feature class %s"%fcname)

        rows = arcpy.SearchCursor(fcname)
        for row in rows:
                yield [row.getValue(x) for x in wanted_fields]

        del rows
        
def polyline_geom_to_pointlist(shape):
        pointlist = []
        if(shape.partCount != 1):
                arcpy.AddError("Error: shape has multiple parts")
                arcpy.AddError("Please run ArcToolbox -> Data Management")
                arcpy.AddError("     -> Features -> Multipart to Singlepart")
                arcpy.AddError(" to fix the input feature class before running sDNA")
                raise StandardError, "Invalid shape"
        
        for point in shape.getPart(0):
                pointlist.append((point.X,point.Y))

        return pointlist

def point_geom_to_point(shape):
        if(shape.partCount != 1):
                arcpy.AddError("Error: shape has multiple parts")
                arcpy.AddError("Please run ArcToolbox -> Data Management")
                arcpy.AddError("     -> Features -> Multipart to Singlepart")
                arcpy.AddError(" to fix the input feature class before running sDNA")
                raise StandardError, "Invalid shape"

        point = shape.getPart(0)
        return point.X, point.Y

startelev_fieldname = "DirectedNode_NegativeOrientation_GradeSeparation"
endelev_fieldname = "DirectedNode_PositiveOrientation_GradeSeparation"

shape_fieldname = "SHAPE"

# read parameters
in_roadlink_class = arcpy.GetParameterAsText(0)
in_node_class = arcpy.GetParameterAsText(1)
out_link_class = arcpy.GetParameterAsText(2)
out_error_class = arcpy.GetParameterAsText(3)

net = Net()

#read roadlinks
for polyline,linkid in read_feature_class(in_roadlink_class,[shape_fieldname,"OSODR"]):
        net.add_bare_link(polyline_geom_to_pointlist(polyline),linkid)

#read connectnodes
for point,nodeid,linkid,level,terminal in read_feature_class(in_node_class,[shape_fieldname,"OSODR","LINK_OSODR","LEVEL","TERMINAL"]):
        net.add_node(point_geom_to_point(point),nodeid,linkid,level,terminal)

arcpy.AddMessage("Linking")
net.build()

# write combined network to feature class
arcpy.AddMessage("Writing to feature class %s"%out_link_class)

arcpy.CreateFeatureclass_management(os.path.dirname(out_link_class),
                                   os.path.basename(out_link_class), 
                                   "Polyline",
                                   spatial_reference=in_roadlink_class)

arcpy.AddField_management(out_link_class,startelev_fieldname,'SHORT')
arcpy.AddField_management(out_link_class,endelev_fieldname,'SHORT')

ic = arcpy.InsertCursor(out_link_class)

line = arcpy.Array()
pnt = arcpy.Point()
for edge in net.get_edges():
    line.removeAll()
    for point in edge.points:
        pnt.X, pnt.Y = point
        line.add(pnt)

    row = ic.newRow()

    row.shape = line
    row.setValue(startelev_fieldname,edge.startelev)
    row.setValue(endelev_fieldname,edge.endelev)
    ic.insertRow(row)
    del row
del ic

# write problem nodes to feature class
arcpy.AddMessage("Writing errors to feature class %s"%out_error_class)

arcpy.CreateFeatureclass_management(os.path.dirname(out_error_class),
                                   os.path.basename(out_error_class), 
                                   "Point",
                                   spatial_reference=in_roadlink_class)
arcpy.AddField_management(out_error_class,"Description",'TEXT',127)
ic = arcpy.InsertCursor(out_error_class)

pnt = arcpy.Point()
for point,text in net.get_problems():
    pnt.X, pnt.Y = point
    row = ic.newRow()

    row.shape = pnt
    row.setValue("Description",text)
    
    ic.insertRow(row)
    del row
del ic
