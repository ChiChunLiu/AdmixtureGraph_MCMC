#!/bin/sh

awk -vOFS=$'\t' '{print $1,$1":"$4,$3,$4,$5,$6,$7,$8}' data/1.bim > tmpbim
mv tmp data/1.bim
awk '{print 0,$1,$3}' data/1.ind > data/1.clst
plink --bfile data/1 --freq --missing --within data/1.clst
gzip plink.frq.strat
python scripts/plink2treemix.py plink.frq.strat.gz treemix.frq.gz
mv treemix.frq.gz data

treemix -i data/treemix.gz -o data/treemix
rm plink.*
