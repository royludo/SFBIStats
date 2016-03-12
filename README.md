# SFBIStats

## CONTENT

1. PROJECT
2. USAGE
3. DETAILS
4. CONTRIBUTE
5. CHANGELOG
6. ACKNOWLEDGEMENTS

## 1. PROJECT

This project aims to:
 - give a programmatic access to data related to the recent bioinformatics job market in France.
 - provide some [basic analysis and charts](https://www.dropbox.com/sh/b33edivf9tuljfw/AABiurGJNg0i0EdhxoEwouc0a) related to those data.

The data come from the [Société Française de Bioinformatique (SFBI)](http://www.sfbi.fr/), an association who, among other things, gathers job
offers and posts them on their [website](http://www.sfbi.fr/recherche_emplois) and mail list.
You will find here information related to more than 1200 job offers that have been posted from april 2012 onward.
The data will be updated every month.

This project concerns data of french origin, and was essentially destined for the french bioinformatics community. 
English has been used for the code, but the output charts are in french.

Please read the details section before using the charts.

## 2. USAGE

### 2.1 Setup the environment

The following procedures assume you have the [conda environment manager](http://conda.pydata.org/docs/) installed.
If you don't, here is the [miniconda download page](http://conda.pydata.org/miniconda.html).

#### 2.1.1 The quick way

Make use of the provided environment definition file `env.yml`

```bash
wget https://raw.githubusercontent.com/royludo/SFBIStats/master/env.yml
conda env create -f env.yml
```

This will setup a complete environment called sfbistatsenv with all the requirements already installed.
Don't forget `source activate sfbistatsenv`

Then go to 2.1.3

#### 2.1.2 The less quick way

Create the environment:

`conda create -n sfbistatsenv python=2.7`

Install the requirements:

```bash
conda install matplotlib
conda install pandas
conda install pymongo
conda install PIL
conda install basemap
pip install geopy
pip install wordcloud
```

Continue with 2.1.3

#### 2.1.3 Get the code

Clone the repository directly in your environment. You should end up with something like `sfbistatsenv/SFBIStats/sfbistats` containing the actual code.

#### 2.1.4 Make Python aware of your project

Make the project's packages available to python:

`export PYTHONPATH="$PYTHONPATH:/path/to/the/envs/sfbistatsenv/SFBIStats"`

### 2.2 Run the script

```bash
mkdir output
python ./sfbistats/analysis/analyze.py --json ./resources/jobs_anon.json --output_dir ./output
```

## 3. DETAILS

### Job corpus

Among the job offers posted on the SFBI mail list, only the formatted ones (posted through the SFBI website) have been
considered, for practical reasons. The SFBI started formatting job offers through their website only in 2012. Before
that, offers were sent and forwarded to the list as is. That is why the dataset starts in april 2012.

But through 2012 and partially 2013, users could keep on sending unformatted offers to the mail list. Those offers don't
appear here. Thus, great care must be taken regarding the interpretation of those data. The increase of job offers must
be put into perspective, as people were switching from the previous anarchic job posts to the formatted one.

Due to different technical issues (crazy encodings, dead links...), a small number of offers do not appear in the
dataset. But as no real bias is introduced by these issues, this should be ok.

### Dataset structure

Each job entry contains the following fields:
 - _id: unique mongodb ID
 - title 
 - submission_date
 - contract_type: 'CDD', 'CDI', 'Stage', 'Thèse'
 - contract_subtype: 'PR', 'MdC', 'CR', 'IR', 'IE', 'CDI autre', 'Post-doc / IR', u'CDD Ingénieur', 'ATER', 'CDD autre'
 - duration
 - city
 - starting_date
 - limit_date
 - validity_date

Stage and Thèse don't have any subtypes, so the contract_subtype field is empty.

### Dataset usage

The file jobs_anon.json contains all the data used in this project. It comes from mongodb, so there are some points to 
be aware of. More information on the specific [strict mode JSON format](https://docs.mongodb.org/manual/reference/mongodb-extended-json/).
The data can be easily parsed nonetheless with:

```python
import json
from bson import json_util

json.loads(jobs_anon.json, object_hook=json_util.object_hook)
```

See the [json_util doc](http://api.mongodb.org/python/1.4/api/pymongo/json_util.html) as pointed out [on this stackoverflow thread](http://stackoverflow.com/a/11286988).

The data have been scraped from web pages, and are delivered raw. Sanitization of the fields is left to users.

### Charts

You can see a sample of the output charts [here](https://www.dropbox.com/sh/b33edivf9tuljfw/AABiurGJNg0i0EdhxoEwouc0a). They are numbered according to the script that created it:
 - summary.py : 1
 - lexical_analysis.py : 2 (unusable with the provided data)
 - time_series.py : 3
 - maps.py : 4
So figure_1_1 and figure_1_2 are the first two figures from summary.py, and so on...

figure_1_5, 3_8 and 3_9:

The education level required for a job has been inferred only from job subtypes, and concerns only CDD and CDI.
Stage and Thèse categories have been excluded.
The job was considered as requiring :
 - a master degree with subtypes 'CDD Ingénieur' and 'IE'
 - a PhD with subtypes 'Post-doc / IR', 'PR', 'MdC', 'CR', 'IR', 'ATER'

The fuzzy subtypes 'CDD autre' and 'CDI autre' have been excluded.
So beware that the information displayed in these charts may not be the most accurate there is. Use with caution.

figure_2_1:

Generated with the [word_cloud module](https://github.com/amueller/word_cloud) using the content of the job offers.

figure_2_2:

This is just an example of what the lexical_analysis module can do.
Some programming languages have been chosen to illustrate it.

figure_2_3:

See figure_2_1. Generated with the titles of the job offers.

### Code

You will probably be interested by the content of the analysis package only. The main script is analyze.py. It calls
the other python modules which produce the charts. 
Beware that lexical_analysis.py can not be used with the provided data.

## 4. CONTRIBUTE

If you want to transform the charts with your own awesome style, if you have a better way to get the data (or more 
data), or if you feel like some different kinds of charts could be useful, then don't hesitate! Fork, code, and tell us
about it. We will happily accept any kind of contribution to this project!

### Example: creating other charts

Feel like the horizontal bar chart could be better if it was... vertical? No problem.
Create your own python module (let's say, myscript.py) and put your code inside a function that looks like

`def run(job_list, output_dir):`

Now you have a list of jobs and a place to output your nice new charts!
Process the data the way you want and save your work in output_dir.
When you're done, open analyze.py, import your script and add

`myscript.run(job_list, output_dir)`

to the end of the code.
Next time you run analyze.py, you will see your own charts added to the others.

### TODO

 - finish the maps
 - more doc
 - improve hbar charts
 - logging

## 5. CHANGELOG

## 6. ACKNOWLEDGEMENTS

Big thanks to the [bioinfo-fr](http://bioinfo-fr.net/) community, who lighted the sparkle of motivation for this project, and Lins` in particular.
Credits for the original data go to the [SFBI](http://www.sfbi.fr/).
