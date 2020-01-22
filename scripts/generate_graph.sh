#!/bin/bash
module load gsl
module load openblas
module load graphviz

# source activate py2
# export PATH="/home/chichun/miniconda3/envs/py2/bin:$PATH"

qpGraph="/project2/jnovembre/ccliu/utils/admixtools/src/qpGraph"
graphwriter="python2 scripts/graph_writer_170718.py"
param_directory="tmp"
data_prefix="$1"
data_directory="data"
param_file="${param_directory}/tmp.par"

echo "DIR: ${data_directory}" > ${param_file}
echo "genotypename: DIR/${data_prefix}.geno" >> ${param_file}
echo "snpname: DIR/${data_prefix}.snp" >> ${param_file}
echo "indivname: DIR/${data_prefix}.ind" >> ${param_file}
echo -e 'outpop: Outgroup\nblgsize: 0.001\ndiag: .0001\nhires: YES' >> ${param_file}
echo -e 'initmix: 1000\nprecision: .0001\nzthresh: 2.0' >> ${param_file}
echo -e 'terse: NO\nuseallsnps: NO' >> ${param_file}

${graphwriter} --pop=Outgroup,S1 > graph/Outgroup.S1.graph
${graphwriter} --in=graph/Outgroup.S1 --pop=S2 --at=b_n000_n002
mv graph/Outgroup.S1.S2.1.graph graph/Outgroup.S1.S2.graph
${graphwriter} --in=graph/Outgroup.S1.S2 --pop=Adm

graph_prefix="graph/Outgroup.S1.S2.Adm.2way.1.graph"
${qpGraph} -p ${param_file} -g ${graph_prefix} -o ${graph_prefix}.out -d ${graph_prefix}.dot | tee ${graph_prefix}.log
dot -Tps < ${graph_prefix}.dot > ${graph_prefix}.ps
