#!/usr/bin/python3

import sys
import csv
import matplotlib.pyplot as plt

welcome_ranking = dict()

with open(sys.argv[1], mode='r') as csv_file:
	csv_reader = csv.DictReader(csv_file)
	
	for row in csv_reader:
		if row['ResponseId'][:2] != 'R_':
			for field in row:
				print(field, row[field])
			
			sys.exit()
		#print(row.keys())
		#print(row['ResponseId'])
		#print()
		#print(row)
		#print()
		
		#if row['Finished'] == 'False': continue
		#print(row['Race'], row['LGBTQIA'])
		#if row['Race'] == '': 
		#	print(row)
		#	sys.exit()
		
		"""
		But also split data by all fields
		"""
		
		race = row['Race']
		lgbt = row['LGBTQIA']
		idmg = row['Identities']
		
		if race == 'Yes' or lgbt == 'Yes' or idmg == 'Yes':
			identities = True
		else: identities = False
		
		citz = row['Citizen']
		intn = row['Internat']
		immg = row['Immig']
		
		citzen_status
		
		year = row['Year']
		
		#print(race)
		#print()
		#sys.exit()
		# Rankings
		
		welcomed = row['Rank Lab_1']
		print(race, year, welcomed)
		if welcomed not in welcome_ranking:
			welcome_ranking[welcomed] = 0
		welcome_ranking[welcomed] += 1
		
		id_welcome = dict()
		
		id_welcome[identities][welcomed] += 1
		
		#print(row.values())
		#sys.exit()
sys.exit()
vals  = list(welcome_ranking.values())
ranks = list(welcome_ranking.keys())
plt.pie(vals, labels=ranks,autopct='%1.2f')
plt.title('Do you feel welcomed?')
plt.show()

"""
individual graphs for agreement per question
graphs for agreement per question by broad categories
	4 graphs, 1 for if yes on identities then another for if No on identities
then graphs for all levels
	x2 for each question and level
"""








