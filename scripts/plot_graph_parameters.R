library(ggplot2)
library(tidyverse)
library(gridExtra)
setwd('~/Desktop/workspace/AdmixtreGraph2020/graph')

prefix = 'standard_rep'

branch_length_ratio = list()
for (i in 1:100){
  branch_df = read_table(
    paste0(prefix, i, '.out'), 
    col_names = c('type', 'branch', 'n0', 'n1', 'val'),
    skip = 15,
    n_max = 9)
  
  # outgroup branches
  b1 <- branch_df %>% 
    filter(branch %in% c('b_n000_n001', 'b_n000_n003')) %>%
    summarise('b_n000_n003' = sum(val)) %>%
    unlist()
  
  # admixture branches
  b2 <- branch_df %>% 
    filter(branch %in% c('b_n005_n006',
                         'b_n007_n008',
                         'b_n009_n010')) %>%
    summarise('b_admixture' = sum(val)) %>%
    unlist()
  
  # other branches
  b3 <- branch_df %>%
    filter(n1 %in% c('n005','n007','n002','n004')) %>%
    select(branch, val) 
  b3_names = b3$branch
  b3 <- unlist(b3$val)
  names(b3) <- b3_names
  
  # merge into a tibble
  branch_length_ratio[[i]] = bind_rows(c(b2, b3)/b1)
}
branch_length_ratio = bind_rows(branch_length_ratio)


scale_constant = 8e5
pars = names(branch_length_ratio)
true_ratio = tibble(par = pars, 
                    val = c(8.5e4, 1.6e5, 1.15e5, 4e4, 8.5e4)/scale_constant)

colMeans(branch_length_ratio)

plots = list()
pars = unique(branch_df$branch)
for (i in seq_along(pars)){
  p = pars[i]
  plots[[i]] <- branch_df %>% 
    filter(branch == p) %>%
    ggplot(., aes(x=val)) +
    geom_density() +
    geom_vline(aes(xintercept=mean(val)),
               color="blue", linetype="dashed", size=1) +
    theme(plot.title = element_text(hjust = 0.5),
          axis.text.x = element_text(angle = 45)) +
    ggtitle(p)
}
do.call("grid.arrange", c(plots, ncol= 3))



admixture_df = list()
for (i in 1:100){
  admixture_df[[i]] = read_table(
    paste0(prefix, i, '.out'), 
    col_names = c('type', 'n0', 'n1', 'n2', 'coef1', 'coef2'),
    skip = 24,
    n_max = 1)
}
admixture_df = bind_rows(admixture_df)





plot <- admixture_df %>% 
  ggplot(., aes(x=coef1)) +
  geom_density() +
  geom_vline(aes(xintercept=mean(coef1)),
             color="blue", linetype="dashed", size=1) +
  theme(plot.title = element_text(hjust = 0.5),
        axis.text.x = element_text(angle = 45)) +
  ggtitle('coef1')
plot
