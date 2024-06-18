#!/usr/bin/Rscript

install.packages("car")
install.packages("stats")
filename = commandArgs(trailingOnly=TRUE)[1]
data = read.table(filename)

suppressPackageStartupMessages(require(car,quietly=TRUE))

for (col in data)
{
	var = col
	p = powerTransform(var)
	cat(sprintf("%f\n",p$lambda["var"]))
}
