#!/bin/sh



awk -vOFS=$'\t' '{print $1,$1":"$4,$3,$4,$5,$6,$7,$8}' data/$1.bim > $1.tmpbim
mv $1.tmpbim data/$1.bim

awk '{print 0,$1,$3}' data/$1.ind > data/$1.clst
plink --bfile data/$1 --freq --missing --within data/$1.clst --out $1
gzip $1.frq.strat 
python scripts/plink2treemix.py $1.frq.strat.gz data/treemix.$1.gz

treemix -i data/treemix.$1.gz -m 1 -o data/treemix.$1
rm $1.*
