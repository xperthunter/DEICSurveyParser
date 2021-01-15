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
			race = row['Race']
			lgbt = row['LGBTQIA']
			idmg = row['Identities']
			citz = row['Citizen']
			intn = row['Internat']
			immg = row['Immig']
			
			for q in surveydata:
				if row[q] not in surveydata[q]['total']:
					surveydata[q]['total'][row[q]] = 0
				surveydata[q]['total'][row[q]] += 1
				"""
				break down by the identity variables
				surveydata[q]['RaceYes/No'][Respnse] += 1
				"""
				

print(json.dumps(surveydata,indent=4))
		
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