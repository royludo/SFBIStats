# SFBIStats

## CONTENT

1. PROJECT
2. REQUIREMENTS
4. USAGE
5. DETAILS
6. CHANGELOG
7. ACKNOWLEDGEMENTS

## 1. PROJECT

This project has two goals:
 - to give a programmatic access to data related to the recent bioinformatics job market in France
 - to provide some basic analysis and charts related to those data

The data come from the French Society of Bioinformatics (SFBI), an association who, among other things, gathers job offers
and posts them on their 
website and mail list. All the data used in this projects are already accessible [here](http://www.sfbi.fr/recherche_emplois).

You will find here information related to more than 1200 job offers that have been posted from april 2012 to this day.
More information on the dataset can be found in the stats files.
Please read the details section before using the charts.

### Remarks

This project concerns data of french origin, and was essentially destined to the french bioinformatics community. 
English has been used for the code, but the output stats and charts are in french. Also, all the files are encoded in UTF-8.

## 5. DETAILS

### Job corpus

Among the job offers posted on the SFBI mail list, only the formatted ones (posted through the SFBI website) have been considered, for practical reasons.
The SFBI started to enforce the use of their website only in 2012.
Before that, offers were sent and forwarded to the list as is.
That is why the dataset only contains offers from april 2012 onward.
Thus, great care must be taken regarding the interpretation of those data.
The increase of job offers must be relativized, as people were switching from the previous anarchic job posts to the formatted one, through 2012 and 2013.

Due to different technical issues (crazy encodings, dead links), a small number of offers do not appear in the dataset.
But as no bias is introduced by these issues, this should be ok.

### Dataset usage

The file jobs.json contains all the data used in this project.
It comes from mongodb, so there are some points to be aware of.
More information on the specific [strict mode JSON format](https://docs.mongodb.org/manual/reference/mongodb-extended-json/).
The data can be easily parsed nonetheless with:

```python
import json
from bson import json_util

json.loads(your_json, object_hook=json_util.object_hook)
```

See [this](http://api.mongodb.org/python/1.4/api/pymongo/json_util.html) as pointed out [on this stackoverflow thread](http://stackoverflow.com/a/11286988).

### Dataset structure

Each entry contains the following fields:
 - _id : unique mongodb ID
 - title : 
 - submission_date : 
 - contract_type : 'CDD', 'CDI', 'Stage', 'Thèse'
 - contract_subtype : 'PR', 'MdC', 'CR', 'IR', 'IE', 'CDI autre', 'Post-doc / IR', u'CDD Ingénieur', 'ATER', 'CDD autre'
 Stage and Thèse don't have any subtypes, so the field is empty ('')
 - duration : empty of not applicable (CDI), -1 if parsing problems
 - city : 
 - starting_date : 
 - limit_date : 
 - validity_date :
 
### Charts

The charts are numbered according to the script that created it:
 - summary.py : 1
 - lexical_analysis.py : 2
 - time_series.py : 3
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
This was generated with the [word_cloud module](https://github.com/amueller/word_cloud).

figure_2_2;
This is just an example of what the lexical_analysis module can do.
Some programming languages have been chosen to illustrate it.

## 4.USAGE

### 4.1 Environment setup

The following procedures assume you have the [conda environment manager](http://conda.pydata.org/docs/) installed.
If you don't, here is the [miniconda download page](http://conda.pydata.org/miniconda.html).

#### 4.1.1 The quick way

Make use of the provided environment definition file `env.yml`:
`conda env create -f env.yml`

This will setup a complete environment called sfbistatsenv with all the requirements already installed.
Go to 4.1.3

#### 4.1.2 The less quick way

Create the environment:
`conda create -n sfbistatsenv python=2.7`

Install the requirements:
conda install matplotlib
conda install pandas
conda install pymongo OR pip install bson
conda install PIL
conda install basemap
pip install geopy
pip install wordcloud

Continue with 4.1.3

#### 4.1.3 Get the code

Create the project's directory (ex: SFBIStats) and clone the repository there.
You should end up with something like sfbistatsenv/SFBIStats/sfbistats containing the actual code.

#### 4.1.4 Make Python aware of your directory

Make the project's packages available to python:
export PYTHONPATH="$PYTHONPATH:/path/to/the/envs/sfbistatsenv/SFBIStats"

### 4.2 Run the script

python ./sfbistats/analayze/analysis.py --json ./resources/jobs_anon.json --output_dir ./output

## 7. ACKNOWLEDGEMENTS

I want to thank the bioinfo-fr community, who motivated me for this project, and Lins` in particular. He also had this idea.
Credits for the original data go to the SFBI.
