#!/usr/bin/python3

import json
import sys
import csv
import matplotlib.pyplot as plt

welcome_ranking = dict()

freeresponse    = {'OtherFR':[], 'Actions':[], 'FreeRep Com':[]}
surveyquestions = dict()
surveydata      = dict()
frontmatter     = ['StartDate', 'EndDate', 'Status', 'Progress', 
				   'Duration (in seconds)', 'Finished', 'RecordedDate',
				   'ResponseId', 'DistributionChannel', 'UserLanguage',
				   'Race', 'LGBTQIA', 'Identities', 'Citizen', 'Internat',
				   'Immig', 'Year']
quals = {'race' : None, 'lgbt' : None, 'idmg' : None, 
		 'cit' : None, 'intn' : None, 'immg' : None, 
		 'idcg' : None, 'cicg' : None}

with open(sys.argv[1], mode='r') as csv_file:
	csv_reader = csv.DictReader(csv_file)
	
	for row in csv_reader:
		if row['ResponseId'][:2] != 'R_':
			for i,field in enumerate(row):
				if field in freeresponse: continue
				if field in frontmatter: continue 
				else:
					if field not in surveyquestions:
						surveyquestions[field] = row[field]
						surveydata[field] = dict()
						surveydata[field]['total'] = dict()
		else:
			# Gather identities
			quals['race'] = row['Race']
			quals['lgbt'] = row['LGBTQIA']
			quals['idmg'] = row['Identities']
			quals['citz'] = row['Citizen']
			quals['intn'] = row['Internat']
			quals['immg'] = row['Immig']
			
			identities = quals['race'] == 'Yes' or quals['lgbt'] == 'Yes' or quals['idmg'] == 'Yes'
			citizen = quals['citz'] == 'Yes' or quals['intn'] == 'Yes' or quals['immg'] == 'Yes'
			quals['idcg'] = identities
			quals['cicg'] = citizen
			
			
			for q in surveydata:
				if row[q] not in surveydata[q]['total']:
					surveydata[q]['total'][row[q]] = 0
				surveydata[q]['total'][row[q]] += 1
				
				for c in quals:
					if c not in surveydata[q]: surveydata[q][c] = dict()
					if quals[c] not in surveydata[q][c]:
						surveydata[q][c][quals[c]] = dict()
					if row[q] not in surveydata[q][c][quals[c]]:
						surveydata[q][c][quals[c]][row[q]] = 0
					
					surveydata[q][c][quals[c]][row[q]] += 1
				

print(json.dumps(surveydata,indent=4))

"""		
for q in surveydata:
	for levels in surveydata[q]:
		for resp
"""	
	

"""
for every question in surveydata:
	vals = surveydata[q]['total'].values()
	ranks  
vals  = list(welcome_ranking.values())
ranks = list(welcome_ranking.keys())
plt.pie(vals, labels=ranks,autopct='%1.2f')
plt.title(surveyquestions[q])
plt.show()

individual graphs for agreement per question
graphs for agreement per question by broad categories
	4 graphs, 1 for if yes on identities then another for if No on identities
then graphs for all levels
	x2 for each question and level
"""