#!/usr/bin/python3

import argparse
import json
import os
import numpy as np
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
quals = {'BIPOC' : None, 'LGBTQIA' : None, 'Marginalized Identities' : None, 
		 'Citizen' : None, 'International' : None, 'Immigrant' : None, 
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
			quals['BIPOC'] = row['Race']
			quals['LGBTQIA'] = row['LGBTQIA']
			quals['Marginalized Identities'] = row['Identities']
			quals['Citizen'] = row['Citizen']
			quals['International'] = row['Internat']
			quals['Immigrant'] = row['Immig']
			
			identities = quals['BIPOC'] == 'Yes' or quals['LGBTQIA'] == 'Yes' or quals['Marginalized Identities'] == 'Yes'
			citizen = quals['Citizen'] == 'Yes' and quals['International'] == 'No' and quals['Immigrant'] == 'No'
			margin  = identities == True or citizen == False
			quals['Identity Group'] = identities
			quals['Citizen Group'] = citizen
			quals['Marginalized Group'] = margin
			
			if len(row['Y/N Discrim']) == 0: row['Y/N Discrim'] = 'NoResponse'
			if len(row['P-B3']) == 0: row['P-B3'] = 'NoResponse'
			
			if row['Y/N Discrim'] not in surveydata['Y/N Discrim']['total']:
				surveydata['Y/N Discrim']['total'][row['Y/N Discrim']] = 0
			
			surveydata['Y/N Discrim']['total'][row['Y/N Discrim']] += 1
			if row['Y/N Discrim'] != 'NoResponse':
				if row['P-B3'] not in surveydata['P-B3']['total']:
					surveydata['P-B3']['total'][row['P-B3']] = 0
				surveydata['P-B3']['total'][row['P-B3']] += 1
			
			yn = 'Y/N Discrim'
			pb3 = 'P-B3'
			for q, k in quals.items():
				if 'vars' not in surveydata: surveydata['vars'] = dict()
				if q not in surveydata['vars']:
					surveydata['vars'][q] = dict()
				if k not in surveydata['vars'][q]:
					surveydata['vars'][q][k] = 0
				
				surveydata['vars'][q][k] += 1
				
				if q not in surveydata[yn]: 
					surveydata[yn][q] = dict()
					surveydata[pb3][q] = dict()
				
				if k not in surveydata[yn][q]:
					surveydata[yn][q][k] = dict()
					surveydata[pb3][q][k] = dict()
				
				if row['Y/N Discrim'] not in surveydata['Y/N Discrim'][q][k]:
					surveydata['Y/N Discrim'][q][k][row['Y/N Discrim']] = 0
				surveydata['Y/N Discrim'][q][k][row['Y/N Discrim']] += 1
				
				if row['Y/N Discrim'] != 'NoResponse':
					if row['P-B3'] not in surveydata['P-B3'][q][k]:
						surveydata['P-B3'][q][k][row['P-B3']] = 0
					surveydata['P-B3'][q][k][row['P-B3']] += 1
			
			for q in surveydata:
				if q == 'Y/N Discrim': continue
				if q == 'P-B3': continue
				if q == 'vars': continue
				if len(row[q]) == 0: row[q] = 'NoResponse'
				if row[q] == 'Prefer not to answer':
					row[q] = 'NoResponse'
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
	json.dump(surveydata, fp, indent=2)

with open('survey_questions.json', 'w') as f:
	json.dump(surveyquestions, f)

#sys.exit()
labels = ['Strongly Agree', 'Somewhat Agree', 'Neither Agree nor Disagree',
		  'Somewhat Disagree', 'Strongly Disagree', 'NoResponse']
#answ = [k.replace(' ','\n') for k in labels]
colors_dic = {'Strongly Agree':'lightseagreen', 'Somewhat Agree':'turquoise', 
		'Neither Agree nor Disagree':'thistle', 'Somewhat Disagree':'palevioletred',
		'NoResponse':'darkgray', 'Strongly Disagree':'crimson'}
pres = []

def pie_slices(dic):
	cmap = plt.get_cmap('Reds')
	a = [k.replace(' ', '\n') for k in sorted(dic.keys()) if k != 'NoResponse']
	v = [dic[k] for k in sorted(dic.keys()) if k != 'NoResponse']
	c = list(cmap(np.linspace(0.25, 0.55, len(a))))
	if 'NoResponse' in dic:
		a.append('NoResponse')
		v.append(dic['NoResponse'])
		c.append('darkgray')
	return a, v, c

def label_organizer(dic, present):
	answ = None
	vals = None
	cols = None
	sep  = False
	if len(present) == 1 and present[0] == 'NoResponse':
		answ, vals, cols = pie_slices(dic) 
		sep = True
		return answ, vals, cols, sep
	elif len(present) == 1 and present[0] != 'NoResponse':
		answ = [k for k in labels if k in present]
		vals = [dic[k] for k in answ]
		cols = [colors_dic[k] for k in answ]
		answ = [k.replace(' ', '\n') for k in answ]
		return answ, vals, cols, sep
	elif len(present) > 1:
		answ = [k for k in labels if k in present]
		vals = [dic[k] for k in answ]
		cols = [colors_dic[k] for k in answ]
		answ = [k.replace(' ', '\n') for k in answ]
		return answ, vals, cols, sep
	else:
		answ, vals, cols = pie_slices(dic) 
		sep = True
		return answ, vals, cols, sep
	
for q in surveydata:
	if q == 'vars': continue
	qname = q
	qname = qname.replace(" ", "_")
	qname = qname.replace("/", "_")
	print(qname)
	head = surveyquestions[q]
	head = re.sub('.+: - ', '', head)
	sep = False
	for level in surveydata[q]:
		print(level)
		if level == 'total':
			pres = []
			pres = [k for k in surveydata[q]['total'].keys() if k in labels]
			
			answers,values,colors,sep = label_organizer(surveydata[q]['total'], pres)
			
			fig, ax = plt.subplots(figsize=(5.25,5.25))
			fig.suptitle(head,wrap=True,fontsize=12)
			if sep:
				ax.pie(values, labels=answers, autopct='%1.1f',
					textprops={'fontsize':8}, colors=colors)
			else:
				ax.pie(values, labels=answers, autopct='%1.1f', 
					textprops={'fontsize':8}, colors=colors)
			
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
			else:
				print(data_keys)
				sys.exit()
			
			fig, axs = plt.subplots(ncols=len(data_keys),nrows=1,figsize=(10.5,5.25))
			fig.suptitle(head,wrap=True,fontsize=12)
			for i, dk in enumerate(dkeys):
				pres = []
				pres = [k for k in surveydata[q][level][dk].keys() if k in labels]
				
				answers,values,colors,sep = label_organizer(surveydata[q][level][dk], pres)			
				
				if sep:
					axs[i].pie(values, labels=answers, autopct='%1.1f',
						textprops={'fontsize':8}, colors=colors)
				else:
					axs[i].pie(values, labels=answers, autopct='%1.1f', 
						textprops={'fontsize':8}, colors=colors)
				
				c = sum(values)
				
				axs[i].title.set_text(f'{level} - {dk}')
				axs[i].text(0,-1.5,f"count: {c}",
					size=10, ha='center')
			
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