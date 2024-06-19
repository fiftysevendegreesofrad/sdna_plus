# (c) Crispin Cooper on behalf of Cardiff University 2015
# This file is released under MIT license

from __future__ import unicode_literals
import sys
import subprocess
from subprocess import Popen,PIPE
import csv,sys,numpy,tempfile,os,copy
from sdna_environment import UnicodeCSVReader,UnicodeCSVWriter,bytes_to_str

SINGLE_BEST="single_best_variable"
MULTIPLE_LASSO="multiple_variables"
MULTIPLE_RIDGE="all_variables"
MODES = "|".join([SINGLE_BEST,MULTIPLE_RIDGE,MULTIPLE_LASSO])

def percent_under(t,data):
    return 100.*len([0 for d in data if d<=t])/len(data)

def GEHTest(preds,ys,env,time_hours):
    truncpreds = [max(1,p) for p in preds]
    truncpreds = [p/time_hours for p in truncpreds]
    ys = [y/time_hours for y in ys]
    gehs = [(2*(p-y)**2/(p+y))**0.5 for p,y in zip(truncpreds,ys)]
    env.AddMessage("GEH time period is %f hours"%time_hours)
    mean_geh = numpy.mean(gehs)
    env.AddMessage(("GEH average (mean): %.2f"%mean_geh))
    env.AddMessage(("    maximum.......: %.2f"%max(gehs)))
    for threshold in [5,10,15,20]:
        env.AddMessage("    <=%2d: %.1f%%"%(threshold,percent_under(threshold,gehs)))
    return gehs
   
def make_positive(datalist):
    MIN = 1
    m = min(datalist)
    if m>=MIN:
        shift = 0
    else:
        shift = MIN-m
    shifted_data = [d+shift for d in datalist]
    return shift,shifted_data


DIR = os.path.dirname(__file__)

if sys.platform=='win32':
    R_COMMAND = os.path.join(DIR,"rportable","R-Portable","App","R-Portable","bin","i386","RScript.exe")
    SHELL_MODE = False
    NO_R_CONSOLE = "--no-Rconsole"
else:
    R_COMMAND = "Rscript"
    SHELL_MODE = True
    NO_R_CONSOLE = ""

def R_call(script,args):
    scriptpath = os.path.join(DIR, script)
    return '"%s" --no-site-file --no-save --no-environ --no-init-file --no-restore %s "%s" %s' % (R_COMMAND,
                                                                                                  NO_R_CONSOLE,
                                                                                                  scriptpath,
                                                                                                  " ".join(args)
                                                                                                 )


def Rcall_estimate(script,arrays,env):
    assert len(arrays)>0
    # write each var to temporary file
    tmpfiles = [tempfile.NamedTemporaryFile(delete=False,mode="w") for _ in arrays]
    for tmpfile,arr in zip(tmpfiles,arrays):
        for row in arr:
            for v in row:
                tmpfile.write("%.15f "%v)
            tmpfile.write("\n")
        tmpfile.write("\n")
        tmpfile.close()
    # call R
    process = subprocess.Popen(R_call(script,['"%s"'%t.name for t in tmpfiles]),shell=SHELL_MODE,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
    result = []
    stdout,stderr = process.communicate()
    stdout = bytes_to_str(stdout,"utf8")
    stderr = bytes_to_str(stderr,"utf8")
    lines = stdout.split('\n')[0:arrays[0].shape[1]]
    if stderr:
        env.AddError("Estimation error ******")
        env.AddError(stderr)
    for line in lines:
        try:
            result.append(float(line))
        except ValueError:
            env.AddWarning("Failed estimation: "+line)
            result.append(None)
    for tmpfile in tmpfiles:
        os.unlink(tmpfile.name)
    return numpy.array(result)

def unpack_regres_output(r_output,env):
    lines = r_output.split("\n")
    in_coefs_section = False
    in_regcurve_section = False
    coefs = []
    regcurve = []
    summarystring="\n"
    for line in lines:
        if line.strip()=="":
            continue
        if line.strip()=="begin regcurve":
            in_regcurve_section = True
            continue
        if line.strip()=="end regcurve":
            in_regcurve_section = False
            continue
        if line.strip()=="Coefficients":    
            in_coefs_section = True
            continue
        if in_coefs_section:
            coefparts = line.strip().split()
            varname,coef = coefparts
            coefs += [(varname,float(coef))]
        elif in_regcurve_section:
            rcparts = line.strip().split(",")
            regcurve += [list(map(float,rcparts))]
        else:
            parts = line.split(",")
            formatted_parts = []
            for p in parts:
                try:
                    p = "%.3f"%float(p)
                except ValueError:
                    pass
                formatted_parts += [p]
            summarystring += ",".join(formatted_parts)+"\n"

    env.AddMessage(summarystring)
    return coefs,regcurve
    
def regularizedregression(data,names,targetdata,targetname,alpha,nfolds,reps,env,weights,intercept,reglambda):
    if len(names)<2:
        env.AddError("Error: multiple variable models need 2 or more predictor variables")
        sys.exit(1)
    tmpfile = tempfile.NamedTemporaryFile(delete=False,mode="w")
    writer = csv.writer(tmpfile)
    writer.writerow([targetname]+names)
    for trow,row in zip(targetdata,data.T):
        writer.writerow([trow]+list(row))
    tmpfile.close()
    weightfile = tempfile.NamedTemporaryFile(delete=False,mode="w")
    weightfile.write(" ".join(["%.15f"%w for w in weights])+"\n")
    weightfile.close()
    xs = "+".join(names)
    if intercept:
        intercept_s="--intercept 1"
    else:
        intercept_s="--intercept 0"
    if reglambda:
        reglambda_s = "--reglambdamin %f --reglambdamax %f"%tuple(reglambda)
    else:
        reglambda_s = ""
    call = R_call("regularizedregression.R",['--calibrationfile "%s" --target %s --xs %s --alpha %f --nfolds %d --reps %d --weightfile "%s" %s %s'
                                                %(tmpfile.name,targetname,xs,alpha,nfolds,reps,weightfile.name,intercept_s,reglambda_s)])
    p = Popen(call,shell=SHELL_MODE,stdout=PIPE,stderr=PIPE,stdin=PIPE)
    stdout,stderr = p.communicate()
    stdout = bytes_to_str(stdout,"utf8")
    stderr = bytes_to_str(stderr,"utf8")
    os.unlink(tmpfile.name)
    os.unlink(weightfile.name)
    coefs,regcurve = unpack_regres_output(stdout,env)
    if coefs and regcurve:
        return coefs,regcurve
    else:
        env.AddError("R call failed")
        env.AddError("STDOUT: *************************")
        env.AddError(stdout)
        env.AddError("STDERR: *************************")
        env.AddError(stderr)
        sys.exit(1)
    
def boxcox_estimate(vars,env):
    return Rcall_estimate("boxcox.R",[vars],env)

def boxtidwell_estimate(x1,x2,y,env):
    return Rcall_estimate("boxtidwell.R",[y,x1,x2],env)
    
def boxcox(data,names,env):
    assert((data>0).all())
    assert len(data.shape)==2
    assert len(names)==data.shape[1]
    lambdas = boxcox_estimate(data,env)
    for L,name in zip(lambdas,names):
        if L==None:
            raise ValueError(name+" failed Box Cox estimation")  # FIXME TRY 1/3 ETC?
    data = boxcox_transform(data,lambdas)
    return data,lambdas

def boxtidwell(xdata_bt,xdata_non_bt,ydata,btnames,env):
    assert type(xdata_bt)==type(numpy.array([]))
    assert type(xdata_non_bt)==type(numpy.array([]))
    assert type(ydata)==type(numpy.array([]))
    assert((xdata_bt>0).all())
    assert len(xdata_bt.shape)==2
    assert len(ydata.shape)==2
    assert ydata.shape[0]==1
    lambdas = boxtidwell_estimate(xdata_bt,xdata_non_bt,ydata,env)
    for L,name in zip(lambdas,btnames):
        if L==None:
            raise ValueError(name+" failed Box Tidwell estimation")  # FIXME
    data = boxcox_transform(xdata_bt,lambdas)
    return data,lambdas
    
boxcox_vectorized=numpy.vectorize(lambda d,t: (numpy.log(d) if t==0 else (pow(d,t)-1)/t) if t!=1 else d)

def boxcox_transform(data,transform):
    '''data: indexed by point then variable
       transform: vector'''
    for d,t in zip(data,transform):
        assert t==1 or (d>0).all()
    assert len(data.shape)==2
    assert len(transform)==data.shape[1]
    t = numpy.tile(transform,(data.shape[0],1))
    result = boxcox_vectorized(data,t)
    assert result.shape==data.shape
    return result
    
def boxcox_inverse_transform(data,transform):
    '''data: vector, transform: scalar'''
    if transform==0:
        return numpy.exp(data)
    elif transform==1:
        return data
    else:
        return pow(data*transform+1,1./transform)

def wmean(xs,ws):
    return numpy.sum(xs*ws)/numpy.sum(ws)
    
def wcov(xs,ys,ws):
    xmean = wmean(xs,ws)
    ymean = wmean(ys,ws)
    return numpy.sum(ws*(xs-xmean)*(ys-ymean))/numpy.sum(ws)
        
def pearson_r(xs,ys,ws):
    return wcov(xs,ys,ws)/(wcov(xs,xs,ws)*wcov(ys,ys,ws))**0.5

def r2(xs,ys,ws):
    return pearson_r(xs,ys,ws)**2
    
def adj_r2(xs,ys,ws):
    n = float(len(ys))
    return 1-(1-(pearson_r(xs,ys,ws)**2))*(n-1)/(n-2) # adjusted r2 from r2 with p=1
    
def univar_regress(xs,ys,ws):
    coeff,intercept = numpy.polyfit(xs,ys,1,w=ws)
    return coeff,intercept

def xval_r2(xs,ys,ws,nfolds,reps):
    xval_resid_squares = numpy.zeros((0))
    xval_weights = numpy.zeros((0))
    for _ in range(reps):
        foldid = numpy.random.permutation([i*nfolds/len(xs) for i in range(len(xs))])
        for f in range(nfolds):
            # fit regression line on folds !=f and test on fold f
            coeff,intercept = univar_regress(xs[foldid!=f],ys[foldid!=f],ws[foldid!=f])
            pred = coeff*xs[foldid==f]+intercept
            xval_resid_squares = numpy.append(xval_resid_squares,(ys[foldid==f]-pred)**2)
            xval_weights = numpy.append(xval_weights,ws[foldid==f])
    mean_resid_square = numpy.average(xval_resid_squares, weights=xval_weights)
    std_resid_square = numpy.average((xval_resid_squares-mean_resid_square)**2, weights=xval_weights)**0.5
    mean_y = numpy.average(ys,weights=ws)
    var_y = numpy.average((ys-mean_y)**2,weights=ws)
    rsquared = 1.-mean_resid_square/var_y
    std_rsquared = std_resid_square/var_y # sic: we are computing error on rsquared, which mirrors previous line
    return rsquared,std_rsquared

def pickbest(data,ws,names,targetdata,nfolds,reps,env):
    results = [{"name":name,
                "xs":d,
                "r":pearson_r(d,targetdata,ws),
                "xvalr2":xval_r2(d,targetdata,ws,nfolds,reps)} for name,d in zip(names,data)]
    results = [r for r in results if not numpy.isnan(r["xvalr2"][0])]
    results.sort(key=lambda x: x["xvalr2"][0])
    env.AddMessage("\n******** Models considered, from worst to best: ********\nVariable, Mean-Xval-R2, Std-of-mean-xval-R2")
    for result in results:
        negstr = "-" if result["r"]<0 else ""
        xvalr2,xvalr2std = result["xvalr2"]
        env.AddMessage(negstr+result["name"]+", %.3f, %.3f"%(xvalr2,xvalr2std/((reps*nfolds)**0.5)))
    best = results[-1]
    xs = best["xs"]
    coeff,intercept = univar_regress(xs,targetdata,ws)
    fitr2 = best["r"]**2
    env.AddMessage("\nBest model R2 = %.3f\nCross-validated R2 = %.3f \n"%(fitr2,xvalr2))
    return [("(Intercept)",intercept),(best["name"],coeff)]

class SdnaRegModel:
    @staticmethod
    def fromParams(targetshift,targetlambda,intercept,vars,varshifts,varlambdas,varcoeffs,regcurve,xstdcoefs):
        rm = SdnaRegModel()
        rm.targetshift = targetshift
        rm.targetlambda = targetlambda
        rm.intercept = intercept
        rm.vars = vars
        rm.varshifts = varshifts
        rm.varlambdas = varlambdas
        rm.varcoeffs = varcoeffs
        rm.regcurve = regcurve
        rm.varstdcoeffs = xstdcoefs
        return rm
        
    def save(self,csvfile):
        with UnicodeCSVWriter(csvfile) as writer:
            self._output(writer)
        if self.regcurve:
            with UnicodeCSVWriter(csvfile+".regcurve.csv") as writer:
                for line in self.regcurve:
                    writer.writerow(line)
    
    def __repr__(self):
        class StringWriter:
            def __init__(self):
                self.output=[]
            def writerow(self,line):
                self.output+=[", ".join(map(str,line))] # ditches full precision
            def __repr__(self):
                return "\n".join(self.output)
        s = StringWriter()
        self._output(s)
        return s.__repr__()
    
    _c_sdna_regression_model = ["sDNA regression model"]
    _c_target_shift = "Target shift"
    _c_target_lambda = "Target lambda"
    _c_intercept = "Intercept"
    _c_varheaders = ["Variable","Shift","Lambda","Coeff","StdCoeff"]
    def _output(self,writer):
        writer.writerow(SdnaRegModel._c_sdna_regression_model)
        writer.writerow([SdnaRegModel._c_target_shift,self.targetshift])
        writer.writerow([SdnaRegModel._c_target_lambda,self.targetlambda])
        writer.writerow([SdnaRegModel._c_intercept,self.intercept])
        writer.writerow([])
        writer.writerow(SdnaRegModel._c_varheaders)
        for name,shift,lam,coeff,stdcoeff in zip(self.vars,self.varshifts,self.varlambdas,self.varcoeffs,self.varstdcoeffs):
            writer.writerow([name,shift,lam,coeff,stdcoeff])
    
    @staticmethod
    def fromFile(filename):
        rm = SdnaRegModel()
        with UnicodeCSVReader(filename) as r:
            header = next(r)
            if header!=SdnaRegModel._c_sdna_regression_model:
                raise Exception("Not a valid model")
            tss,ts = next(r)
            if tss!=SdnaRegModel._c_target_shift:
                raise Exception("Not a valid model")
            rm.targetshift = float(ts)
            tls,tl = next(r)
            if tls!=SdnaRegModel._c_target_lambda:
                raise Exception("Not a valid model")
            rm.targetlambda = float(tl)
            ints,i = next(r)
            if ints!=SdnaRegModel._c_intercept:
                raise Exception("Not a valid model")
            rm.intercept = float(i)
            next(r)
            varheaders=next(r)
            if varheaders!=SdnaRegModel._c_varheaders:
                if varheaders!=SdnaRegModel._c_varheaders[:-1]: #allow old models without final column
                    raise Exception("Not a valid model")
            rm.vars = []
            rm.varshifts = []
            rm.varlambdas = []
            rm.varcoeffs = []
            rm.varstdcoeffs = []
            for line in r:
                if len(line)==len(SdnaRegModel._c_varheaders)-1:
                    line+=["0"] #allow old models without final column
                name,shift,lam,coeff,stdcoeff = line
                rm.vars += [name]
                rm.varshifts += [float(shift)]
                rm.varlambdas += [float(lam)]
                rm.varcoeffs += [float(coeff)]
                rm.varstdcoeffs += [float(stdcoeff)]
        return rm
            
    def getVarNames(self):
        return self.vars
        
    def predict(self,data):
        '''Takes data by rows then variable (in order specified by getVarNames())'''
        assert data.shape[1]==len(self.vars)
        data = data.copy()
        data = data + self.varshifts
        data = boxcox_transform(data,self.varlambdas)
        data = data * self.varcoeffs
        data = data.sum(axis=1)
        data = data + self.intercept
        data = boxcox_inverse_transform(data,self.targetlambda)
        data = data - self.targetshift
        return data

    @staticmethod
    def fromData(ydata,xdatadict,x_order,yname,mode,nfolds,reps,bctarget,btregex,bcregex,env,weightlambda,gehtime,use_intercept,reglambda):
        unchanged_xdatadict = copy.copy(xdatadict)
        unchanged_ydata = copy.copy(ydata)
        
        assert sorted(x_order)==sorted(xdatadict.keys())
        ydata = numpy.array(ydata).copy() 
        
        # check data length
        datalen = len(ydata)
        x_data_lengths = [len(x) for x in xdatadict.values()]
        for dl in x_data_lengths:
            assert dl==datalen
        env.AddMessage(str(datalen)+" data points")

        #if nfolds*3 > datalen:
        #    raise ValueError("Not enough data for %d-fold cross validation: try reducing number of folds"%nfolds)
        
        # apply box tidwell regex
        btnames = [n for n in x_order if btregex.match(n)] if btregex else []
        if btnames:
            bt_non_transformed_names = [n for n in x_order if not btregex.match(n)]
            env.AddMessage("Variables for Box-Tidwell transformation: %s"%",".join(btnames))
        
        # apply box cox regex
        bcnames = [n for n in x_order if bcregex.match(n)] if bcregex else []
        if bcnames:
            env.AddMessage("Variables for Box-Cox transformation: %s"%",".join(bcnames))
        
        # shift data if needed
        if bctarget or btnames:
            yshift,ydata = make_positive(ydata)
            if yshift>0:
                env.AddMessage("Target variable contains values less than 1 and has been shifted")
        else:
            yshift = 0
        
        if btnames or bcnames:
            xshifts = {}
            for n in list(xdatadict.keys()):
                shift,data = make_positive(xdatadict[n])
                xdatadict[n] = data
                xshifts[n] = shift
        else:
            xshifts = {n:0 for n in list(xdatadict.keys())}
        shifted_xs = [n for n in x_order if xshifts[n]>0]
        if shifted_xs:
            env.AddMessage("The following predictor variables contained values less than 1 and have been shifted: %s"%",".join(shifted_xs))
        
        # transform y data if needed
        if bctarget:
            env.SetProgressor("default","Transforming y data",0)
            # package up ydata in [ydata] so it matches dimensionality of xs for transformations
            ydata,ylambda = boxcox(numpy.array([ydata]).T, [yname], env)
            ydata,ylambda = ydata.T[0],ylambda[0]
        else:
            ylambda = 1
        
        # transform x data if needed
        xlambdas = {n:1 for n in x_order}
        if btnames:
            env.SetProgressor("default","Box-Tidwell transforming x data",0)
            xdata_bt = numpy.array([xdatadict[n] for n in btnames])
            xdata_non_bt = numpy.array([xdatadict[n] for n in bt_non_transformed_names])
            xdata_bt, btlambda = boxtidwell(xdata_bt,xdata_non_bt,numpy.array([ydata]),btnames,env)
            for n,lamb,d in zip(btnames,btlambda,xdata_bt):
                xlambdas[n]=lamb
                xdatadict[n]=d
        if bcnames:
            env.SetProgressor("default","Box-Cox transforming x data",0)
            xdata_bc = numpy.array([xdatadict[n] for n in bcnames]).T
            xdata_bc, bclambda = boxcox(xdata_bc,bcnames,env)
            xdata_bc = xdata_bc.T
            for n,lamb,d in zip(bcnames,bclambda,xdata_bc):
                xlambdas[n]=lamb
                xdatadict[n]=d
            
        # convert x data to numpy array
        xdata_arr = numpy.array([xdatadict[n] for n in x_order])
                
        weights = numpy.array([(y+1)**(weightlambda-1) for y in ydata])
        
        # test models
        env.SetProgressor("step","Testing models (don't worry if this appears to hang)",1)
        env.SetProgressorPosition(0)
        regcurve = None
        if mode==SINGLE_BEST:
            coefs = pickbest(xdata_arr,weights,x_order,ydata,nfolds,reps,env)
        elif mode==MULTIPLE_LASSO:
            coefs,regcurve = regularizedregression(xdata_arr,x_order,ydata,yname,1,nfolds,reps,env,weights,use_intercept,reglambda)
        elif mode==MULTIPLE_RIDGE:
            coefs,regcurve = regularizedregression(xdata_arr,x_order,ydata,yname,0,nfolds,reps,env,weights,use_intercept,reglambda)
        else:
            assert(False)
         
        if (coefs[0][0]=="(Intercept)"):
            intercept = coefs[0][1]
            coefs = coefs[1:]
        else:
            intercept = 0

        # ditch varibles with coefficient=0
        xnames = [c[0] for c in coefs if c[1]!=0]
        xcoeffs = [c[1] for c in coefs if c[1]!=0]
        
        xshifts = [xshifts[n] for n in xnames]
        xlambdas = [xlambdas[n] for n in xnames]

        xstddict = {n:numpy.array(xdatadict[n]).std() for n in x_order}
        ystd = ydata.std()
        xstdcoefs = [c*xstddict[n]/ystd for c,n in zip(xcoeffs,xnames)]
        
        model = SdnaRegModel.fromParams(yshift,ylambda,intercept,xnames,xshifts,xlambdas,xcoeffs,regcurve,xstdcoefs)
        
        # do GEH test of model
        wanted_fields = model.getVarNames() 
        gehdata = []
        for i in range(len(unchanged_ydata)):
            gehdata += [[unchanged_xdatadict[f][i] for f in wanted_fields]]
        gehdata = numpy.array(gehdata) # indexed by row then var
        preds = model.predict(gehdata)
        gehs = GEHTest(preds,unchanged_ydata,env,gehtime)

        return model,preds,gehs
