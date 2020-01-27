import momi
import os
import logging
import argparse
logging.basicConfig(level=logging.INFO,
                    filename="tutorial.log")
os.chdir('/Users/chichun/Desktop/workspace/AdmixtreGraph2020')

parser = argparse.ArgumentParser()
parser.add_argument('--replicate', '-r', type=str, help='replicate')
args = parser.parse_args()
replicate_id = args.replicate

# simulating Data
recoms_per_gen = 1.25e-8
bases_per_locus = int(5e6)
n_loci = 100
ploidy = 2  

# n_alleles per population (n_individuals = n_alleles / ploidy)
sampled_n_dict = {"Outgroup": 4,"S1":8, "S2":8, "Adm":8}


# a dict mapping samples to populations
ind2pop = {}
for pop, n in sampled_n_dict.items():
    for i in range(int(n / ploidy)):
        ind2pop["{}_{}".format(pop, i)] = pop

with open("data/ind2pop.txt", "w") as f:
    for i, p in ind2pop.items():
        print(i, p, sep="\t", file=f)


bashCommand = "python -m momi.read_vcf data/{0}.vcf.gz data/ind2pop.txt data/{0}.snpAlleleCounts.gz --bed data/{0}.bed".format(replicate_id)
os.system(bashCommand)

bashCommand = "python -m momi.extract_sfs data/sfs_{0}.gz 100 data/{0}.snpAlleleCounts.gz".format(replicate_id)
os.system(bashCommand)

sfs = momi.Sfs.load("data/sfs_{}.gz".format(replicate_id))

no_pulse_model = momi.DemographicModel(N_e=5e4, gen_time=29, muts_per_gen=1.25e-8)
no_pulse_model.set_data(sfs)
# random initial value; user-specified lower bound
no_pulse_model.add_time_param("t_Adm_S2", lower=1e4)
no_pulse_model.add_leaf("Adm")
no_pulse_model.add_leaf("S2")
no_pulse_model.move_lineages("Adm", "S2", t="t_Adm_S2")
no_pulse_model.add_leaf("S1")
no_pulse_model.add_time_param("t_anc", lower=5e4, lower_constraints=["t_Adm_S2"])
no_pulse_model.move_lineages("S2", "S1", t="t_anc")
no_pulse_model.add_leaf("Outgroup")
no_pulse_model.add_time_param("t_out", lower_constraints=["t_anc"])
no_pulse_model.move_lineages("S1", "Outgroup", t="t_out")
add_pulse_model = no_pulse_model.copy()
add_pulse_model.add_pulse_param("p_pulse")
add_pulse_model.move_lineages(
    "Adm", "GhostS1", t=4.5e4, p="p_pulse")
add_pulse_model.add_time_param(
    "t_ghost", lower=5e4,
    upper_constraints=["t_anc"])
add_pulse_model.move_lineages(
    "GhostS1", "S1", t="t_ghost")
add_pulse_model = no_pulse_model.copy()
add_pulse_model.add_pulse_param("p_pulse")
add_pulse_model.add_time_param(
    "t_pulse", upper_constraints=["t_Adm_S2"])
add_pulse_model.move_lineages(
    "Adm", "GhostS1", t="t_pulse", p="p_pulse")
add_pulse_model.add_time_param(
    "t_ghost", lower_constraints=["t_pulse"], 
    upper_constraints=["t_anc"])
add_pulse_model.move_lineages(
    "GhostS1", "S1", t="t_ghost")

results = []
n_runs = 1
for i in range(n_runs):
    add_pulse_model.set_params(
        # parameters inherited from no_pulse_model are set to their previous values
        no_pulse_model.get_params(),
        # other parmaeters are set to random initial values
        randomize=True)

    results.append(add_pulse_model.optimize(options={"maxiter":200}))

# sort results according to log likelihood, pick the best (largest) one
best_result = sorted(results, key=lambda r: r.log_likelihood)[-1]

add_pulse_model.set_params(best_result.parameters)
best_result

pars = best_result.parameters
outfile = 'output/momi_rep{}.txt'.format(replicate_id)
if os.path.exists(outfile):
    os.remove(outfile)
with open(outfile, 'a') as output:
    for p in pars:
        output.write('{0}\t{1}\n'.format(p, str(float(pars[p]))))


