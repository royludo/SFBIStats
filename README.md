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

We highly recommend to use the [conda environment manager](http://conda.pydata.org/docs/) to install and use this project.

### 2.1 Setup

The following procedures assume you have already installed conda.
If you don't, here is the [miniconda download page](http://conda.pydata.org/miniconda.html).

#### 2.1.1 Create the virtual environment

Make use of the provided environment definition file `env.yml`

```bash
wget https://raw.githubusercontent.com/royludo/SFBIStats/master/env.yml
conda env create -f env.yml
```

This will setup a complete environment called sfbistatsenv with the core package requirements already installed.
Don't forget `source activate sfbistatsenv`

#### 2.1.2 Get the code

Clone the repository directly in your environment. You will end up with a folder `sfbistatsenv/SFBIStats` containing 
all the project.

#### 2.1.4 Install the package

Go in the project's directory.
`python setup.py install`

### 2.2 Run the examples

You probably want to use the data and create some charts. The examples folders contains scripts that make use of the 
SFBI jobs data to produce charts as seen [here](http://bioinfo-fr.net/etat-de-lemploi-bioinformatique-en-france-analyse-des-offres-de-la-sfbi) or [here](https://www.dropbox.com/sh/b33edivf9tuljfw/AABiurGJNg0i0EdhxoEwouc0a).
Each folder is different, and has its own dependencies. Please refer to the README provided in each folder for instructions
on how to install and run each example.

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

You can see a sample of the output charts [here](https://www.dropbox.com/sh/b33edivf9tuljfw/AABiurGJNg0i0EdhxoEwouc0a).
They are named according to the script that created it.

summary_5 and 10, time_series_8 and 9, summary_lins_6 and 7:

The education level required for a job has been inferred only from job subtypes, and concerns only CDD and CDI.
Stage and Thèse categories have been excluded.
The job was considered as requiring :
 - a master degree with subtypes 'CDD Ingénieur' and 'IE'
 - a PhD with subtypes 'Post-doc / IR', 'PR', 'MdC', 'CR', 'IR', 'ATER'

The fuzzy subtypes 'CDD autre' and 'CDI autre' have been excluded.
So beware that the information displayed in these charts may not be the most accurate there is. Use with caution.

lexical_analysis 1-11:

Generated with the [word_cloud module](https://github.com/amueller/word_cloud) using the titles of the job offers.
Types and subtypes of contracts are specified in each image title. 

## 4. CONTRIBUTE

If you want to transform the charts with your own awesome style, if you have a better way to get the data (or more 
data), or if you feel like some different kinds of charts could be useful, then don't hesitate! Fork, code, and tell us
about it. We will happily accept any kind of contribution to this project!

## 5. ACKNOWLEDGEMENTS

Big thanks to the [bioinfo-fr](http://bioinfo-fr.net/) community, who lighted the sparkle of motivation for this
project, and Lins` in particular.
Credits for the original data go to the [SFBI](http://www.sfbi.fr/).
