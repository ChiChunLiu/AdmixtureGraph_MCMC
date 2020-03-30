setwd('~/Desktop/workspace/AdmixtreGraph2020/')
library(tidyverse)
library(glue)
library(gridExtra)

all_models = list()
for (m in 1:3){
  all_models[[m]] = list()
  for (r in 1:100){
    logfile = glue('output/model_{m}.rep{r}.log.txt')
    all_models[[m]][[r]] = read_tsv(logfile)
  }
}

all_models <- all_models %>% map(bind_rows)
names(all_models) <- c('huge_gap', 'small_gap_recent', 'small_gap_ancient')
all_models

plot_likelihood <- function(x){
  name = names(x)
  p <- x[[1]] %>%
    filter(parameter == 'log_likelihood') %>%
    ggplot(aes(x = value)) +
      geom_density(aes(fill = model)) +
      ggtitle(name) +
      theme(axis.text.x = element_text(angle = 45))
  return(list(p))
}

plots = lmap(all_models, plot_likelihood)
do.call("grid.arrange", c(plots, ncol= 3))


model1 <- all_models[[2]] %>% 
  filter(model == 'model_1', parameter == 'log_likelihood')
model2 <- all_models[[2]] %>% 
  filter(model == 'model_2', parameter == 'log_likelihood')
diff = tibble(diff = model1$value - model2$value)diff %>%
ggplot(aes(x = diff)) +
  geom_density() +
  ggtitle('log-likelihood difference') +
  theme(axis.text.x = element_text(angle = 45))


model1 <- all_models[[3]] %>% 
  filter(model == 'model_1', parameter == 'log_likelihood')
model2 <- all_models[[3]] %>% 
  filter(model == 'model_2', parameter == 'log_likelihood')
diff = tibble(diff = model1$value - model2$value)
diff %>%
  ggplot(aes(x = diff)) +
  geom_density() +
  ggtitle('log-likelihood difference') +
  theme(axis.text.x = element_text(angle = 45))
  


