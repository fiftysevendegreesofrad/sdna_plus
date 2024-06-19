#!/usr/bin/Rscript

yfilename = commandArgs(trailingOnly=TRUE)[1]
xfilename = commandArgs(trailingOnly=TRUE)[2]
x2filename = commandArgs(trailingOnly=TRUE)[3]
y = read.table(yfilename)
x = read.table(xfilename)

x2 = NULL
result <- try(function() x2=read.table(x2filename))

suppressPackageStartupMessages(require(car,quietly=TRUE))

if (is.null(x2))
{
    bt = boxTidwell(as.matrix(y)[,1],x1=as.matrix(x))
} else {
    bt = boxTidwell(as.matrix(y)[,1],x1=as.matrix(x),x2=as.matrix(x2))
}

for (lambda in bt$result[,3]) # third column contains lambda
{
	cat(sprintf("%f\n",lambda))
}
