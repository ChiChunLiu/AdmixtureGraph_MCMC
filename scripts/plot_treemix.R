setwd("/project2/jnovembre/ccliu/utils/AdmixtreGraph2020") 

library(RColorBrewer)
library(R.utils)
source("scripts/plotting_funcs.R")

prefix="data/treemix"
png(filename="data/fig/treemix.png")
plot_tree(cex=0.8, prefix)
dev.off()
