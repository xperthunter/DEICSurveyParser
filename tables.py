#!/usr/bin/python3 

import csv
import json
import re
import sys
# test
from pytablewriter import MarkdownTableWriter

labels = ['Strongly Agree', 'Somewhat Agree', 'Neither Agree nor Disagree',
		  'Somewhat Disagree', 'Strongly Disagree', 'NoResponse', 'Prefer not to answer']
names = {'race': 'Race', 'lgbt': 'LGBTQIA', 'idmg': 'Marginalized Identity',
		 'citz': 'Citizen', 'intn': 'International', 'immg': 'Immigrant'}

with open(sys.argv[1], 'r') as fp:
	data = json.load(fp)
	
with open(sys.argv[2], 'r') as fp:
	questions = json.load(fp)

vvm = []
for q in sorted(data['vars'].keys()):
	if q in names:
		qn = names[q]
	else: qn = q
	if 'Yes' in data['vars'][q]:
		vvm.append([qn,data['vars'][q]['Yes'],data['vars'][q]['No']])
	else:
		vvm.append([qn,data['vars'][q]['true'],data['vars'][q]['false']])

writer = MarkdownTableWriter(
	table_name="Identity Variables",
	headers=["Variable", "Yes Count", "No Count"],
	value_matrix=vvm,
	margin=1
)

writer.write_table()

print()
for q in data:
	if q == 'vars': continue
	title=questions[q]
	title = re.sub('.+: - ', '', title)
	vvm = []
	opts = sorted(data[q]['total'].keys())
	row = ['Total']
	d   = [data[q]['total'][k] for k in opts]
	row.extend(d)
	vvm.append(row)
	for level in sorted(data[q].keys()):
		if level == 'total': continue
		
		for ans in sorted(data[q][level].keys()):
			if level not in names: name = level+' - '+ans
			else:                  name = names[level]+' - '+ans
			row = [name]
			d = []
			for opt in opts:
				if opt not in data[q][level][ans]:
					d.append(0)
				else:
					d.append(data[q][level][ans][opt])
			row.extend(d)
			vvm.append(row)
	h = ["Variable"]
	h.extend(opts)
	writer = MarkdownTableWriter(
		table_name=title,
		headers=h,
		value_matrix=vvm,
		margin=1
	)
	writer.write_table()
	print()	
