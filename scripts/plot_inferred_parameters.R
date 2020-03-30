library(ggplot2)
library(tidyverse)
library(gridExtra)
setwd('~/Desktop/workspace/AdmixtreGraph2020/output/')


parameter_df = list()
for (i in 1:100){
  parameter_df[[i]] = read_tsv(paste0('standard_rep', i, '.txt'),
                             col_names = c('rep', 'par', 'val'))
}
parameter_df = bind_rows(parameter_df)
pars = unique(parameter_df$par)
true_pars = tibble(par = pars,
                   val = c(8.5e4,2e5,5e5,0.3,4e4,4e4))


plots = list()
for (i in seq_along(pars)){
  p = pars[i]
  true_val = unlist(true_pars %>% filter(par == p) %>% select(val))
  print(p)
  print(true_val)
  plots[[i]] <- parameter_df %>% 
    filter(par == p) %>%
    ggplot(., aes(x=val)) +
      geom_histogram() +
      geom_vline(data = true_pars %>% filter(par == p),
                 aes(xintercept=val),
                 color="blue", linetype="dashed", size=1) +
    theme(plot.title = element_text(hjust = 0.5),
          axis.text.x = element_text(angle = 45)) +
    ggtitle(p)
}
do.call("grid.arrange", c(plots, ncol= 3))



parameter_df = list()
for (i in 1:100){
  if (file.exists(paste0('standard_rep', i, '.txt'))){
    parameter_df[[i]] = read_tsv(paste0('standard_rep', i, '.txt'),
                                 col_names = c('rep', 'par', 'val'))
  }
}
parameter_df = bind_rows(parameter_df)
pars = unique(parameter_df$par)
true_pars = tibble(par = pars,
                   val = c(8.5e4,2e5,5e5,0.3,4e4,4e4))


plots = list()
for (i in seq_along(pars)){
  p = pars[i]
  true_val = unlist(true_pars %>% filter(par == p) %>% select(val))
  print(p)
  print(true_val)
  plots[[i]] <- parameter_df %>% 
    filter(par == p) %>%
    ggplot(., aes(x=val)) +
    geom_density() +
    geom_vline(data = true_pars %>% filter(par == p),
               aes(xintercept=val),
               color="blue", linetype="dashed", size=1) +
    theme(plot.title = element_text(hjust = 0.5),
          axis.text.x = element_text(angle = 45)) +
    ggtitle(p)
}
do.call("grid.arrange", c(plots, ncol= 3))

