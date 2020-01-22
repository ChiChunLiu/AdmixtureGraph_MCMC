#!/bin/sh

module load plink 
module load gsl
module load openblas

convertf="/project2/jnovembre/ccliu/utils/admixtools/src/convertf"
tmppar=$(mktemp par.XXXXXX)

make_convertf_par () {
    echo "genotypename:    $1.bed" > $tmppar
    echo "snpname:         $1.bim" >> $tmppar
    echo "indivname:       $1.fam" >> $tmppar
    echo "outputformat:    EIGENSTRAT" >> $tmppar
    echo "genotypeoutname: $1.geno" >> $tmppar
    echo "snpoutname:      $1.snp" >> $tmppar
    echo "indivoutname:    $1.ind" >> $tmppar
    echo "familynames:     NO" >> $tmppar
}


plink --vcf $1.vcf.gz \
    --const-fid 0 \
    --keep-allele-order \
    --recode \
    --make-bed \
    --out $1

make_convertf_par $1
$convertf -p $tmppar

pop="S2 S2 S2 S2 Adm Adm Adm Adm S1 S1 S1 S1"
echo $pop | tr ' \t' '\n' > $1.pop.tmp

awk '{print $1,$2}' $1.ind | paste - $1.pop.tmp > $1.tmp
mv $1.tmp $1.ind

rm $tmppar
