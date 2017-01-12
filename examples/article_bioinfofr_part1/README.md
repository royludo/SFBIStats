Charts that have been created for the [first bioinfo-fr article](http://bioinfo-fr.net/etat-de-lemploi-bioinformatique-en-france-analyse-des-offres-de-la-sfbi).

## 1. INSTALL

```bash
conda install matplotlib
conda install pandas
```

## 2. USAGE

```bash
mkdir output
python ./examples/article_bioinfofr_part1/analyze.py --json ./resources/jobs_anon.json --output_dir ./output
```
