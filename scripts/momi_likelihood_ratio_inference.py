import momi
import os
import argparse

# parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--prefix', '-p', type=str, help='prefix of files')
parser.add_argument('--replicate', '-r', type=str, help='replicate')
args = parser.parse_args()
prefix = args.prefix
rep = args.replicate

sampled_n_dict = {"A": 6,"B": 6, "C": 6}
ploidy = 2 
# a dict mapping samples to populations
ind2pop = {}
for pop, n in sampled_n_dict.items():
    for i in range(int(n / ploidy)):
        ind2pop["{}_{}".format(pop, i)] = pop

if not os.path.exists('data/3pops_ind2pop.txt'):
    with open("data/3pops_ind2pop.txt", "w") as f:
        for i, p in ind2pop.items():
            print(i, p, sep="\t", file=f)

# reading in sfs from data
bashCommand = "python -m momi.read_vcf data/{0}{1}.vcf.gz data/3pops_ind2pop.txt data/{0}{1}.snpAlleleCounts.gz --bed data/{0}{1}.bed".format(prefix, rep)
os.system(bashCommand)
bashCommand = "python -m momi.extract_sfs data/sfs_{0}{1}.gz 100 data/{0}{1}.snpAlleleCounts.gz".format(prefix, rep)
os.system(bashCommand)
sfs = momi.Sfs.load("data/sfs_{0}{1}.gz".format(prefix, rep))

# start inference
# model 1: ((A, B),C)
model = momi.DemographicModel(N_e=1e4, gen_time=29, muts_per_gen=1.25e-8)
model.set_data(sfs)
model.add_leaf("A")
model.add_leaf("B")
model.add_leaf("C")
model.add_time_param("t_A_B")
model.add_time_param("t_B_C", lower_constraints=["t_A_B"])
model.move_lineages("A", "B", t="t_A_B")
model.move_lineages("B", "C", t="t_B_C")
model.optimize()

with open(f'output/{prefix}{rep}.log.txt', 'w') as logfile:
    param_dict = model.get_params()
    logfile.write(f'model\tparameter\tvalue\n')
    for p in param_dict:
        logfile.write(f'model_1\t{p}\t{param_dict[p]:.4f}\n')
    logfile.write(f'model_1\tlog_likelihood\t{model.log_likelihood():.4f}\n')

# model 2: (A,(B,C))
model = momi.DemographicModel(N_e=1e4, gen_time=29, muts_per_gen=1.25e-8)
model.set_data(sfs)
model.add_leaf("A")
model.add_leaf("B")
model.add_leaf("C")
model.add_time_param("t_C_B")
model.add_time_param("t_B_A", lower_constraints=["t_C_B"])
model.move_lineages("C", "B", t="t_C_B")
model.move_lineages("B", "A", t="t_B_A")
model.optimize()

with open(f'output/{prefix}{rep}.log.txt', 'a') as logfile:
    param_dict = model.get_params()
    for p in param_dict:
        logfile.write(f'model_2\t{p}\t{param_dict[p]:.4f}\n')
    logfile.write(f'model_2\tlog_likelihood\t{model.log_likelihood():.4f}\n')

# model 3: (B,(A,C))
model = momi.DemographicModel(N_e=1e4, gen_time=29, muts_per_gen=1.25e-8)
model.set_data(sfs)
model.add_leaf("A")
model.add_leaf("B")
model.add_leaf("C")
model.add_time_param("t_C_A")
model.add_time_param("t_A_B", lower_constraints=["t_C_A"])
model.move_lineages("C", "A", t="t_C_A")
model.move_lineages("A", "B", t="t_A_B")
model.optimize()

with open(f'output/{prefix}{rep}.log.txt', 'a') as logfile:
    param_dict = model.get_params()
    for p in param_dict:
        logfile.write(f'model_3\t{p}\t{param_dict[p]:.4f}\n')
    logfile.write(f'model_3\tlog_likelihood\t{model.log_likelihood():.4f}\n')
