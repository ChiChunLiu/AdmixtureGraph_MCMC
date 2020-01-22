setwd("/project2/jnovembre/ccliu/utils/AdmixtreGraph2020") 

library(RColorBrewer)
library(R.utils)
source("scripts/plotting_funcs.R")

prefix="data/treemix"
plot_tree(cex=0.8, prefix)
plot_resid(stem=paste0(prefix,".",edge),pop_order="dogs.list")
