#!/usr/bin/python3

import argparse
import json
import os
import re
import sys
import csv
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='DEIC Survey Parser and Plotter')
parser.add_argument('--csv','-c', required=True, type=str,
	metavar='<str>', help='survey csv')
parser.add_argument('--dir', '-d', required=True, type=str, 
	help='directory to store images')

arg = parser.parse_args()

welcome_ranking = dict()

freeresponse    = {'OtherFR':[], 'Actions':[], 'FreeRep Com':[], 'O-Q1':[],
					'O-Q2':[],'Transportation':[], 'P-M5':[], 'P-M4':[],
					'P-M2':[],'P-B':[], 'P-B4':[], 'P-B2':[], 'P-D5':[],
					'P-D4':[],'P-D2':[], 'P-B5':[]}
surveyquestions = dict()
surveydata      = dict()
frontmatter     = ['StartDate', 'EndDate', 'Status', 'Progress', 
				   'Duration (in seconds)', 'Finished', 'RecordedDate',
				   'ResponseId', 'DistributionChannel', 'UserLanguage',
				   'Race', 'LGBTQIA', 'Identities', 'Citizen', 'Internat',
				   'Immig', 'Year']
quals = {'race' : None, 'lgbt' : None, 'idmg' : None, 
		 'citz' : None, 'intn' : None, 'immg' : None, 
		 'Identity Group' : None, 'Citizen Group' : None}

with open(arg.csv, mode='r') as csv_file:
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
			citizen = quals['citz'] == 'No' or quals['intn'] == 'Yes' or quals['immg'] == 'Yes'
			margin  = quals['race'] == 'Yes' or quals['lgbt'] == 'Yes' or quals['idmg'] == 'Yes' or quals['citz'] == 'No' or quals['intn'] == 'Yes' or quals['immg'] == 'Yes'
			quals['Identity Group'] = identities
			quals['Citizen Group'] = citizen
			quals['Marginalized Group'] = margin
			
			for q, k in quals.items():
				if 'vars' not in surveydata: surveydata['vars'] = dict()
				if q not in surveydata['vars']:
					surveydata['vars'][q] = dict()
				if k not in surveydata['vars'][q]:
					surveydata['vars'][q][k] = 0
				
				surveydata['vars'][q][k] += 1
			
			for q in surveydata:
				if q == 'vars': continue
				if len(row[q]) == 0: row[q] = 'NoResponse'
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
				
with open('survey_data.json', 'w') as fp:
	json.dump(surveydata, fp)

with open('survey_questions.json', 'w') as f:
	json.dump(surveyquestions, f)

#sys.exit()
labels = ['Strongly Agree', 'Somewhat Agree', 'Neither Agree nor Disagree',
		  'Somewhat Disagree', 'Strongly Disagree', 'NoResponse', 'Prefer not to answer']
#answ = [k.replace(' ','\n') for k in labels]
colors = {'Strongly Agree':'lightseagreen', 'Somewhat Agree':'turquoise', 
		'Neither Agree nor Disagree':'thistle', 'Somewhat Disagree':'palevioletred',
		'NoResponse':'darkgray', 'Strongly Disagree':'crimson',
		'Prefer not to answer':'grey'}
pres = []
skip = False
for q in surveydata:
	if q == 'vars': continue
	qname = q
	qname = qname.replace(" ", "_")
	qname = qname.replace("/", "_")
	print(qname)
	head = surveyquestions[q]
	head = re.sub('.+: - ', '', head)
	for level in surveydata[q]:
		if level == 'total':
			pres = [k for k in surveydata[q]['total'].keys() if k in labels]
			if len(pres) > 0:
				answ = [k for k in labels if k in pres]
				vals = [surveydata[q]['total'][k] for k in answ]
				cols = [c for k,c in colors.items() if k in answ]
				answ = [k.replace(' ', '\n') for k in answ]
			else:
				answ = [k.replace(' ', '\n') for k in surveydata[q]['total'].keys()]
				vals = [v for v in surveydata[q]['total'].values()]
			
			 
			fig, ax = plt.subplots(figsize=(5.25,5.25))
			fig.suptitle(head,wrap=True,fontsize=12)
			if len(pres) > 0:
				print(answ)
				print(pres)
				ax.pie(vals, labels=answ, autopct='%1.1f', 
					textprops={'fontsize':6}, colors=cols)
			else:
				ax.pie(vals, labels=answ, autopct='%1.1f',
					textprops={'fontsize':6})
			
			fig.tight_layout()
			filename = os.path.join(arg.dir,qname+'_total.png')
			fig.savefig(filename,dpi=200)
			plt.close()
		else:
			data_keys = []
			for k in surveydata[q][level].keys():
				if k is None: continue
				if type(k) is bool:
					data_keys.append(k)
					continue
				if len(k) == 0: continue
				data_keys.append(k)
			
			print(data_keys)
			if 'Yes' in data_keys: dkeys = ['Yes', 'No']
			elif type(data_keys[0]) == bool: dkeys = [True, False]
			
			fig, axs = plt.subplots(ncols=len(data_keys),nrows=1,figsize=(10.5,5.25))
			fig.suptitle(head,wrap=True,fontsize=12)
			for i, dk in enumerate(dkeys):
				pres = [k for k in surveydata[q][level][dk].keys() if k in labels]
				if len(pres) > 0:
					answ = [k for k in labels if k in pres]
					vals = [surveydata[q][level][dk][k] for k in answ]
					cols = [c for k,c in colors.items() if k in answ]
					answ =[k.replace(' ', '\n') for k in answ]
				else:
					answ = [k.replace(' ', '\n') for k in surveydata[q][level][dk].keys()]
					vals = [v for v in surveydata[q][level][dk].values()]			
				
				if len(pres) > 0:
					axs[i].pie(vals, labels=answ, autopct='%1.1f', 
						textprops={'fontsize':6}, colors=cols)
				else:
					axs[i].pie(vals, labels=answ, autopct='%1.1f',
						textprops={'fontsize':6})
				
				axs[i].title.set_text(f'{level} - {dk}')
			
			filename = os.path.join(arg.dir,qname+'_'+level+'.png')
			fig.savefig(filename,dpi=200)
			plt.close()
"""
Sorting the agreement level
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