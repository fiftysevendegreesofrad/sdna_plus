from __future__ import print_function
from make_barnsbury import *
from ctypes import *
import sys,os
from collections import defaultdict
import arcscriptsdir
import sdnapy
sdnapy.set_dll_path(os.environ["sdnadll"])
from sdnapy import my_void_p

from load_library import load_library

def ensure_unicode(x):
  if sys.version_info < (3, 0):
    return unicode(x)
  return str(x,"ascii")

#sys.stdin.readline()

WARNINGCALLBACKFUNCTYPE = CFUNCTYPE(c_int, c_char_p)
def warning(x):
    if type(x)!=str:
        x = str(x,"ascii")
    print (x)
    return 0
warning_callback = WARNINGCALLBACKFUNCTYPE(warning)

dllpath = os.environ["sdnadll"]
dll = load_library(dllpath)

def add_polyline_inner(net,arcid,points,_gs,weight,cost,isisland):
        point_array_x = (c_double*len(points))()
        point_array_y = (c_double*len(points))()
        for i,(x,y) in enumerate(points):
            point_array_x[i] = x
            point_array_y[i] = y
        dll.net_add_polyline(net,arcid,len(points),point_array_x,point_array_y)
        dll.net_add_polyline_data(net,arcid,b"start_gs",c_float(_gs[0]))
        dll.net_add_polyline_data(net,arcid,b"end_gs",c_float(_gs[1]))
        dll.net_add_polyline_data(net,arcid,b"weight",c_float(weight))
        dll.net_add_polyline_data(net,arcid,b"cost",c_float(cost))
        dll.net_add_polyline_data(net,arcid,b"island",c_float(isisland))
        dll.net_add_polyline_text_data(net,arcid,b"sametext",c_char_p(b"1"))
        dll.net_add_polyline_text_data(net,arcid,b"difftext",c_char_p(str(arcid).encode("ascii")))

def add_polyline(net,arcid,points,start_gs,end_gs,isisland):
    add_polyline_inner(net,arcid,points,(start_gs,end_gs),1,1,isisland)

def add_unlink(net,points):
        point_array_x = (c_double*len(points))()
        point_array_y = (c_double*len(points))()
        for i,(x,y) in enumerate(points):
            point_array_x[i] = x
            point_array_y[i] = y
        dll.net_add_unlink(net,len(points),point_array_x,point_array_y)

def output(net,data="start_gs,end_gs,weight,cost,island",textdata="sametext,difftext"):
    n = sdnapy.Net()
    n.net = net
    print (n.toString(data=data,textdata=textdata))
    n.net = None

print ("minimal split link, absolute weights")

dll.net_create.restype = my_void_p
dll.prep_create.restype = my_void_p
net = dll.net_create()
prep = dll.prep_create(net,b"start_gs=start_gs;end_gs=end_gs;island=island;islandfieldstozero=weight,cost;data_absolute=weight,cost;data_text=sametext,difftext",warning_callback)
add_polyline(net,0,[(0,0),(0,1)],0,0,0)
add_polyline(net,1,[(0,1),(0,2)],0,0,0)
dll.prep_bind_network_data(prep)
print ("before")
output(net)
print ("detect")
dll.prep_get_split_link_ids.restype=c_long
split_link_id_set = POINTER(c_long)()
num_split_link_ids = dll.prep_get_split_link_ids(prep,byref(split_link_id_set))
print (list(split_link_id_set[0:num_split_link_ids]))
print ("repair")
dll.prep_fix_split_links.restype=c_long
print (dll.prep_fix_split_links(prep),"split links repaired")
output(net)
dll.net_destroy(net)
print ()

print ("minimal split link, length weighted")

net = (dll.net_create())
prep = (dll.prep_create(net,b"start_gs=start_gs;end_gs=end_gs;island=island;islandfieldstozero=weight,cost;data_unitlength=weight,cost;data_text=sametext,difftext",warning_callback))
add_polyline(net,0,[(0,0),(0,1)],0,0,0)
add_polyline(net,1,[(0,1),(0,2)],0,0,0)
dll.prep_bind_network_data(prep)
print ("before")
output(net)
print ("detect")
dll.prep_get_split_link_ids.restype=c_long
split_link_id_set = POINTER(c_long)()
num_split_link_ids = dll.prep_get_split_link_ids(prep,byref(split_link_id_set))
print (list(split_link_id_set[0:num_split_link_ids]))
print ("repair")
dll.prep_fix_split_links.restype=c_long
print (dll.prep_fix_split_links(prep),"split links repaired")
output(net)
dll.net_destroy(net)
dll.calc_destroy(prep)
print ()

print ("minimal traffic island")
net = (dll.net_create())
prep = (dll.prep_create(net,b"start_gs=start_gs;end_gs=end_gs;island=island;islandfieldstozero=weight,cost;data_absolute=weight,cost;data_text=sametext,difftext",warning_callback))
add_polyline(net,0,[(0,0),(0,1)],0,0,0)
add_polyline(net,1,[(0,1),(0,2),(0,3)],0,0,1)
add_polyline(net,2,[(0,1),(1,2),(0,3)],0,0,1)
add_polyline(net,3,[(0,3),(0,4)],0,0,0)
add_polyline(net,4,[(0,4),(0,5)],0,0,0)
dll.prep_bind_network_data(prep)
print ("before")
output(net)
print ("detect")
dll.prep_get_traffic_islands.restype=c_long
traffic_islands = POINTER(c_long)()
num_traffic_islands = dll.prep_get_traffic_islands(prep,byref(traffic_islands))
print (list(traffic_islands[0:num_traffic_islands]))
print ("repair")
dll.prep_fix_traffic_islands.restype=c_long
print (dll.prep_fix_traffic_islands(prep),"traffic islands repaired")
output(net)
dll.net_destroy(net)
dll.calc_destroy(prep)
print ()

print ("dual traffic island")
net = (dll.net_create())
prep = (dll.prep_create(net,b"start_gs=start_gs;end_gs=end_gs;island=island;islandfieldstozero=weight,cost;data_absolute=weight,cost;data_text=sametext,difftext",warning_callback))
add_polyline(net,0,[(0,0),(0,1)],0,0,0)
add_polyline(net,1,[(0,1),(0,2),(0,3)],0,0,1)
add_polyline(net,2,[(0,1),(1,2),(0,3)],0,0,1)
add_polyline(net,3,[(0,3),(0,4)],0,0,0)
add_polyline(net,4,[(0,4),(0,5),(0,6)],0,0,1)
add_polyline(net,5,[(0,4),(1,5),(0,6)],0,0,1)
add_polyline(net,6,[(0,6),(0,7)],0,0,0)
dll.prep_bind_network_data(prep)
print ("before")
output(net)
print ("detect")
dll.prep_get_traffic_islands.restype=c_long
traffic_islands = POINTER(c_long)()
num_traffic_islands = dll.prep_get_traffic_islands(prep,byref(traffic_islands))
print (list(traffic_islands[0:num_traffic_islands]))
print ("repair")
dll.prep_fix_traffic_islands.restype=c_long
print (dll.prep_fix_traffic_islands(prep),"traffic islands repaired")
output(net)
dll.net_destroy(net)
dll.calc_destroy(prep)
print ()


print ("minimal duplicate link")
net = (dll.net_create())
prep = (dll.prep_create(net,b"start_gs=start_gs;end_gs=end_gs;island=island;islandfieldstozero=weight,cost;data_absolute=weight,cost;data_text=sametext,difftext",warning_callback))
add_polyline(net,0,[(0,0),(0,1)],0,0,0)
add_polyline(net,1,[(0,0),(0,1)],0,0,0)
dll.prep_bind_network_data(prep)
print ("before")
output(net)
print ("detect")
dll.prep_get_duplicate_links.restype=c_long
duplicates = POINTER(c_long)()
originals = POINTER(c_long)()
num_duplicates = dll.prep_get_duplicate_links(prep,byref(duplicates),byref(originals))
print (list(zip(list(duplicates[0:num_duplicates]),list(originals[0:num_duplicates]))))
print ("repair")
dll.prep_fix_duplicate_links.restype=c_long
print (dll.prep_fix_duplicate_links(prep),"duplicate links removed")
output(net)
dll.net_destroy(net)
dll.calc_destroy(prep)
print ()

print ("reverse duplicate link")
net = (dll.net_create())
prep = (dll.prep_create(net,b"start_gs=start_gs;end_gs=end_gs;island=island;islandfieldstozero=weight,cost;data_absolute=weight,cost;data_text=sametext,difftext",warning_callback))
add_polyline(net,0,[(0,0),(0,1)],0,0,0)
add_polyline(net,1,[(0,1),(0,0)],0,0,0)
dll.prep_bind_network_data(prep)
print ("before")
output(net)
print ("detect")
dll.prep_get_duplicate_links.restype=c_long
duplicates = POINTER(c_long)()
originals = POINTER(c_long)()
num_duplicates = dll.prep_get_duplicate_links(prep,byref(duplicates),byref(originals))
print (list(zip(list(duplicates[0:num_duplicates]),list(originals[0:num_duplicates]))))
print ("repair")
dll.prep_fix_duplicate_links.restype=c_long
print (dll.prep_fix_duplicate_links(prep),"duplicate links removed")
output(net)
dll.net_destroy(net)
dll.calc_destroy(prep)
print ()

print ("minimal isolated system")
net = (dll.net_create())
prep = (dll.prep_create(net,b"start_gs=start_gs;end_gs=end_gs;island=island;islandfieldstozero=weight,cost;data_absolute=weight,cost;data_text=sametext,difftext",warning_callback))
add_polyline(net,0,[(0,0),(0,1)],0,0,0)
add_polyline(net,1,[(0,1),(0,2)],0,0,0)
add_polyline(net,2,[(1,0),(1,1)],0,0,0)
dll.prep_bind_network_data(prep)
print ("before")
output(net)
print ("detect")
dll.prep_get_subsystems.restype=c_long
links = POINTER(c_long)()
message = c_char_p()
num_disconnected_links = dll.prep_get_subsystems(prep,byref(message),byref(links))
print (ensure_unicode(message.value))
print (list(links[0:num_disconnected_links]))
print ("repair")
dll.prep_fix_subsystems.restype=c_long
print (dll.prep_fix_subsystems(prep),"subsystems removed")
output(net)
dll.net_destroy(net)
dll.calc_destroy(prep)
print ()

print ("minimal near miss connection")
print ("links 0 and 1 should join")
print ("links 2 3 and 4 should join")
print ("link 5 and 6 should not")
net = (dll.net_create())
prep = (dll.prep_create(net,b"start_gs=start_gs;end_gs=end_gs;island=island;islandfieldstozero=weight,cost;data_absolute=weight,cost;;data_text=sametext,difftext;arcxytol=0.2",warning_callback))
add_polyline(net,0,[(0,0),(0,1)],0,0,0)
add_polyline(net,1,[(0,1.1),(0,2)],0,0,0)
add_polyline(net,2,[(0,2),(0,3)],0,0,0)
add_polyline(net,3,[(0,3.15),(0,4)],0,0,0)
add_polyline(net,4,[(0,3.3),(1,4)],0,0,0)
add_polyline(net,5,[(0,4),(0,5)],0,0,0)
add_polyline(net,6,[(0,4.3),(1,5)],0,0,0)
dll.prep_bind_network_data(prep)
print ("before")
output(net)
print ("detect")
dll.prep_get_near_miss_connections.restype=c_long
links = POINTER(c_long)()
num_near_misses = dll.prep_get_near_miss_connections(prep,byref(links))
print (list(links[0:num_near_misses]))
print ("repair")
dll.prep_fix_near_miss_connections.restype=c_long
print (dll.prep_fix_near_miss_connections(prep),"near connections fixed")
output(net)
dll.net_destroy(net)
dll.calc_destroy(prep)
print ()

print ("near miss connection resulting in zero length link")
net = (dll.net_create())
prep = (dll.prep_create(net,b"start_gs=start_gs;end_gs=end_gs;island=island;islandfieldstozero=weight,cost;data_absolute=weight,cost;;data_text=sametext,difftext;arcxytol=0.2",warning_callback))
add_polyline(net,0,[(0,0),(0,0.1)],0,0,0)
dll.prep_bind_network_data(prep)
print ("before")
output(net)
print ("repair")
dll.prep_fix_near_miss_connections.restype=c_long
print (dll.prep_fix_near_miss_connections(prep),"near connections fixed")
output(net)
dll.net_destroy(net)
dll.calc_destroy(prep)
print ()

print ("traffic island unsplits into loop link")
net = (dll.net_create())
prep = (dll.prep_create(net,b"start_gs=start_gs;end_gs=end_gs;island=island;islandfieldstozero=weight,cost;data_absolute=weight,cost;data_text=sametext,difftext",warning_callback))
add_polyline(net,0,[(0,0),(0,1)],0,0,1)
add_polyline(net,1,[(0,0),(1,0)],0,0,1)
add_polyline(net,2,[(0,1),(1,0)],0,0,0)
dll.prep_bind_network_data(prep)
print ("before")
output(net)
print ("detect")
dll.prep_get_traffic_islands.restype=c_long
traffic_islands = POINTER(c_long)()
num_traffic_islands = dll.prep_get_traffic_islands(prep,byref(traffic_islands))
print (list(traffic_islands[0:num_traffic_islands]))
print ("repair")
dll.prep_fix_traffic_islands.restype=c_long
print (dll.prep_fix_traffic_islands(prep),"traffic islands repaired")
output(net)
dll.net_destroy(net)
dll.calc_destroy(prep)
print ()

print ("link unlink import test")
net1 = (dll.net_create())
prep = (dll.prep_create(net1,b"start_gs=start_gs;end_gs=end_gs;island=island;islandfieldstozero=weight,cost;data_absolute=weight,cost",warning_callback))
linkid = 0
def make_line(x1,y1,x2,y2):
        global linkid
        add_polyline(net1,linkid,[(x1,y1),(x2,y2)],0,0,False)
        linkid += 1

def make_little_unlink(x,y):
        r=0.1
        add_unlink(net1,[(x-r,y-r),(x+r,y-r),(x+r,y+r),(x-r,y+r),(x-r,y-r)])

make_line(0,0,1,1) 
make_line(1,0,0,1) #crossroads
make_line(1,1,2,1)
make_line(2,0,2,2) #t junc
make_little_unlink(10.5,0.5)
make_line(10,0,11,1)
make_line(11,0,10,1) #crossroads unlink
make_little_unlink(12,1)
make_line(11,1,12,1)
make_line(12,0,12,2) #t junc unlink
make_line(3,3,6,6)
make_line(4,4,5,5) #duplicate link section

dll.prep_bind_network_data(prep)
print ("before")
output(net1)
dll.prep_import_from_link_unlink_format.restype = my_void_p
net2 = (dll.prep_import_from_link_unlink_format(prep))
print ("after")
output(net1)
print ("result")
output(net2,"","")
dll.net_destroy(net1)
dll.net_destroy(net2)
dll.calc_destroy(prep)

print ("\nempty link unlink import")
net1 = (dll.net_create())
prep = (dll.prep_create(net1,b"",warning_callback))
dll.prep_bind_network_data(prep)
print ("before")
output(net1)
dll.prep_import_from_link_unlink_format.restype = my_void_p
net2 = (dll.prep_import_from_link_unlink_format(prep))
print ("result")
output(net2,"","")
dll.net_destroy(net1)
dll.net_destroy(net2)
dll.calc_destroy(prep)

print ("\nbigger link unlink test")
net1 = (dll.net_create())
prep = (dll.prep_create(net1,b"start_gs=start_gs;end_gs=end_gs;island=island;islandfieldstozero=weight,cost;data_absolute=weight,cost",warning_callback))
netsize=20
for i in range(netsize):
        make_line(i,0,i,netsize)
        make_line(0,i,netsize,i)
dll.prep_bind_network_data(prep)
print ("before")
output(net1)
dll.prep_import_from_link_unlink_format.restype = my_void_p
net2 = (dll.prep_import_from_link_unlink_format(prep))
print ("result")
output(net2,"","")
dll.net_destroy(net1)
dll.net_destroy(net2)
dll.calc_destroy(prep)

print ("\nunlinks only test")
net1 = (dll.net_create())
prep = (dll.prep_create(net1,b"",warning_callback))
make_little_unlink(0,0)
dll.prep_bind_network_data(prep)
print ("before")
output(net1)
dll.prep_import_from_link_unlink_format.restype = my_void_p
net2 = (dll.prep_import_from_link_unlink_format(prep))
print ("result")
output(net2,"","")
dll.net_destroy(net1)
dll.net_destroy(net2)
dll.calc_destroy(prep)
