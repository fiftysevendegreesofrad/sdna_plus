import ctypes
import sys,os

#sys.stdin.readline()

# http://stackoverflow.com/questions/17840144/why-does-setting-ctypes-dll-function-restype-c-void-p-return-long
class my_void_p(ctypes.c_void_p):
    pass

sdnadll = os.environ["sdnadll"]
dll = ctypes.windll.LoadLibrary(sdnadll)

# now using strings rather than enum so this looks a bit tautological, but:
(ANGULAR, EUCLIDEAN, CUSTOM, HYBRID) = ("ANGULAR","EUCLIDEAN","CUSTOM","HYBRID")

current_net_arcids = None

# dummy progress bar callback func
CALLBACKFUNCTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_long)
def set_progressor(x):
    return 0
set_progressor_callback = CALLBACKFUNCTYPE(set_progressor)
WARNINGCALLBACKFUNCTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p)
def warning(x):
    print(str(x,"ascii"))
    return 0
warning_callback = WARNINGCALLBACKFUNCTYPE(warning)

def add_polyline(net,arcid,points):
    global current_net_arcids
    current_net_arcids += [arcid]
    point_array_x = (ctypes.c_double*len(points))()
    point_array_y = (ctypes.c_double*len(points))()
    for i,(x,y) in enumerate(points):
        point_array_x[i] = x
        point_array_y[i] = y
    dll.net_add_polyline(net,arcid,len(points),point_array_x,point_array_y)

def add_polyline_3d(net,arcid,points):
    global current_net_arcids
    current_net_arcids += [arcid]
    point_array_x = (ctypes.c_double*len(points))()
    point_array_y = (ctypes.c_double*len(points))()
    point_array_z = (ctypes.c_float*len(points))()
    for i,(x,y,z) in enumerate(points):
        point_array_x[i] = x
        point_array_y[i] = y
        point_array_z[i] = z 
    dll.net_add_polyline_3d(net,arcid,len(points),point_array_x,point_array_y,point_array_z)

def add_polyline_data(net,link,name,data):
    dll.net_add_polyline_data(net,ctypes.c_long(link),ctypes.c_char_p(name.encode("ascii")),ctypes.c_float(data))

def choice_test(net):
    add_polyline(net,10,[(0,3),(0,0),(1,0),(1,1),(2,1),(2,0),(3,0),(3,1),(4,1),(4,0),(5,0)])
    add_polyline(net,11,[(0,3),(10,3),(10,2),(5,2),(5,0)])
    add_polyline(net,12,[(0,3),(0,103)])
    add_polyline(net,13,[(5,0),(105,0)])
    add_polyline_data(net,10,"one",1)

def height_test(net):
    add_polyline_3d(net,20,[(0,0,0),(1,0,0)])
    add_polyline_3d(net,21,[(1,0,0),(2,0,1)]) # stair
    add_polyline_3d(net,22,[(2,0,1),(3,0,1)]) # stair top
    add_polyline_3d(net,23,[(1,0,0),(1,1,1)]) # escalator (2-way)
    add_polyline_3d(net,24,[(1,1,1),(2,1,1)]) # escalator top
    add_polyline_data(net,23,"is_escalator",1)

def height_test_invert(net):
    add_polyline_3d(net,20,[(0,0,-0),(1,0,-0)])
    add_polyline_3d(net,21,[(1,0,-0),(2,0,-1)]) # stair
    add_polyline_3d(net,22,[(2,0,-1),(3,0,-1)]) # stair top
    add_polyline_3d(net,23,[(1,0,-0),(1,1,-1)]) # escalator (2-way)
    add_polyline_3d(net,24,[(1,1,-1),(2,1,-1)]) # escalator top
    add_polyline_data(net,23,"is_escalator",1)

def oneway_conflict_test(net):
    add_polyline_3d(net,0,[(0,0,0),(0,0,1)])
    add_polyline_data(net,0,"one",1)
    add_polyline_data(net,0,"minusone",-1)

def ambig_oneway_test(net):
    add_polyline(net,0,[(0,0),(1,0)])
    add_polyline_data(net,0,"one",1)
    add_polyline_data(net,0,"se",0)
    add_polyline_data(net,0,"ee",1)

def simple_oneway(net):
    add_polyline(net,1,[(0,0),(1,0)])
    add_polyline(net,2,[(1,0),(2,0)])
    add_polyline(net,3,[(2,0),(3,0)])
    add_polyline_data(net,1,"oneway",0)
    add_polyline_data(net,2,"oneway",1)
    add_polyline_data(net,3,"oneway",0)
    add_polyline_data(net,1,"weight",1)
    add_polyline_data(net,2,"weight",0)
    add_polyline_data(net,3,"weight",1)

def cycle_formula_test(net):
    #3 traffics + bike lane high traffic
    #3 slopes
    #offroad
    for i in range(7):
        add_polyline(net,i,[(i,0),(i,1)])
        add_polyline_data(net,i,"carnet",1)
        add_polyline_data(net,i,"start_gs",0)
    add_polyline_data(net,1,"aadt",15000)
    add_polyline_data(net,2,"aadt",25000)
    add_polyline_data(net,3,"aadt",25000)
    add_polyline_data(net,3,"bikeroute",1)
    add_polyline_data(net,4,"end_gs",0.03)
    add_polyline_data(net,5,"end_gs",0.06)
    add_polyline_data(net,6,"carnet",0)

def test_net(net_definition,config):
    global current_net_arcids
    current_net_arcids = []

    dll.net_create.restype = my_void_p
    net = dll.net_create()
    
    dll.integral_calc_create.restype = my_void_p
    calculation = dll.integral_calc_create(net,ctypes.c_char_p(config.encode("ascii")),
                                                           set_progressor_callback,
                                                           warning_callback)

    if not calculation:
        print ("config failed")
        print ()
        return
    print ("calc created with config",config)
    
    dll.icalc_get_all_output_names.restype = ctypes.POINTER(ctypes.c_char_p)
    dll.icalc_get_output_length.restype = ctypes.c_int
    outlength = dll.icalc_get_output_length(calculation)
    names = dll.icalc_get_all_output_names(calculation)
    names = [str(x,"ascii") for x in names[0:outlength]]
    dll.icalc_get_short_output_names.restype = ctypes.POINTER(ctypes.c_char_p)
    shortnames = dll.icalc_get_short_output_names(calculation)
    sn=[]
    for i in range(outlength):
        sn += [str(shortnames[i],"ascii")]

    dll.calc_expected_data_net_only.restype = ctypes.c_int
    expected_names_no = ctypes.POINTER(ctypes.c_char_p)()
    expected_names_no_length = dll.calc_expected_data_net_only(calculation,ctypes.byref(expected_names_no))
    expected_names_no = [str(x,"ascii") for x in expected_names_no[0:expected_names_no_length]]
    print("expected names net only:",expected_names_no)
    
    
    net_definition(net)

    success = dll.calc_run(calculation)
    
    dll.net_print(net)
    
    if success:
        print('\nshortnames: '+','.join(sn))
        print('created output buffer size float *',outlength)

        print('\nOUTPUT DATA:')

        # for debug display we want to invert output arrays
        out_buffer_type = ctypes.c_float * outlength
        out_buffer = out_buffer_type()
        out_array = []
        for i in current_net_arcids:
            dll.icalc_get_all_outputs(calculation,out_buffer,i)
            out_array += [list(out_buffer)]
            
        print ("arcid"+' '*(35-len("arcid"))+'  '.join("%.6g"%link_data for link_data in current_net_arcids))
        for i in range(outlength):
            print(names[i]+' '*(35-len(names[i]))+'  '.join("%.6g"%link_data[i] for link_data in out_array))

        print('\n')

    print('destroying')
    dll.net_destroy(net)
    dll.calc_destroy(calculation)
    print('done')
    print('\n')

test_net(choice_test,"radii=5,6,10,50,63,n;cont;metric=hybrid;lineformula=euc+ang;juncformula=ang")
test_net(choice_test,"radii=n;cont;metric=hybrid;lineformula=euc;juncformula=_a=PREVone,_a")

#this one should fail
test_net(choice_test,"radii=n;cont;metric=hybrid;lineformula=euc;juncformula=_a=PREVone,a")

#test with oversample
test_net(choice_test,"radii=5,6,10,50,63,n;cont;metric=hybrid;lineformula=euc+ang;juncformula=ang;oversample=3")

test_net(height_test,"radii=n;metric=hybrid;lineformula=euc+(is_escalator?0:hg)")
#invert and check it works for hl
test_net(height_test_invert,"radii=n;metric=hybrid;lineformula=euc+(is_escalator?0:hl)")

# oneway conflict tests
test_net(oneway_conflict_test,"oneway=one")
test_net(oneway_conflict_test,"vertoneway=one")
test_net(oneway_conflict_test,"oneway=one;vertoneway=one")
test_net(oneway_conflict_test,"oneway=one;vertoneway=minusone")
test_net(oneway_conflict_test,"oneway=minusone;vertoneway=one")
print ("ambig oneway")
test_net(ambig_oneway_test,"vertoneway=one")
print ("ambig oneway defeated by _gs field")
test_net(ambig_oneway_test,"vertoneway=one;start_gs=se;end_gs=ee")
test_net(simple_oneway,"oneway=oneway;weight=weight")
test_net(ambig_oneway_test,"vertoneway=nonexist")
test_net(cycle_formula_test,"end_gs=end_gs;start_gs=start_gs;linkonly;metric=hybrid;lineformula= _upslope = hg/FULLeuc*100, _slopefac = _upslope<2?1:(_upslope<4?1.371:(_upslope<6?2.203:4.239)), _aadtfac = (aadt<10000 || bikeroute)?1:(aadt<20000?1.368:(aadt<30000?2.4:8.157)), _bpfac = carnet?1:0.84, euc*_slopefac*_aadtfac*_bpfac + 67.2*ang/90; juncformula = 67.2*ang/90")
test_net(cycle_formula_test,"end_gs=end_gs;start_gs=start_gs;linkonly;metric=cycle")
test_net(cycle_formula_test,"end_gs=end_gs;start_gs=start_gs;linkonly;metric=vehicle")
test_net(cycle_formula_test,"end_gs=end_gs;start_gs=start_gs;linkonly;metric=pedestrian")
