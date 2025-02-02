#!/usr/bin/env python

'''
Author: Astrid Blaauw
Date: 16/01/2016

Script to process table file, containing studies linked to species,
from here we trace every (super)kingdom from every species
(with help of the NCBI taxonomy).

Pipeline study_species table input:
    study_ID species_count species_ID(,species_ID)

(Super)kingdom table output:
	kingdom_ID species_count study_count study_ID(, study_ID)

Usage:
    -i  Text file containing study_ID's linked to species_ID list
    -n  NCBI taxdmp nodes file
'''

import argparse
import itertools
import os
import sys
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def proc_log(logmessage, logtype, log_file):
	if logtype == "inf":
		logging.info(logmessage)
		log_file.write("INFO: " + logmessage + "\n")
	if logtype == "war":
		logging.warning(logmessage)
		log_file.write("WARNING: " + logmessage + "\n")


class TaxNode:
	'''NCBI node class'''

	def __init__(self, taxid, parentid, rank):
		self.taxid = taxid
		self.parentid = parentid
		self.rank = rank

	def get_taxid(self):
		return self.taxid

	def get_parentid(self):
		return self.parentid

	def get_rank(self):
		return self.rank


def get_dict(table):
	'''
	Input:
		File name, for table -
		study_ID species_count species_ID(,species_ID)
	Output:
		dict {study_id : [species_count, [species_ID, species_ID]] }
	'''
	table_file = open(table)
	species = dict()
	for l in table_file:
		l = l.split()
		study_id = l[0]
		if len(l) < 3:
			species_list = [l[1], ["1"]]
		else:
			species_list = [l[1], l[2].split(",")]
		species[study_id] = species_list
	table_file.close()
	return(species)

def get_nodes_objects(nodedmp):
	'''
	Input:
		NCBI nodes.dmp
	Output:
		dict {node_id : node_object}
	'''
	nodes_file = open(nodedmp)
	nodes = dict()
	for i in nodes_file:
		line = i.split("|")
		node_id = line[0].strip()
		parent_id = line[1].strip()
		rank = line[2].strip()
		nodes[node_id] = TaxNode(node_id, parent_id, rank)
	nodes_file.close()
	return nodes


def main():

	parser = argparse.ArgumentParser(description='Process commandline arguments')
	parser.add_argument("-i", type=str,
    	                help="Input file (*.dat file from pipeline, containing MRP matrix/matrices)")
	parser.add_argument("-n", type=str,
    	                help="NCBI taxdmp nodes file")
	args = parser.parse_args()
	
	#outname_log = args.o + args.i
	#outname_log = outname_log.replace(".dat", ".log")
	#log_file = open(outname_log, "a")

	species_dict = get_dict(args.i)		
	unique_species = list()

	kingdoms_table = {"2":[0, list()], "2157":[0, list()], "33208":[0, list()], "33090":[0, list()], "4751":[0, list()], "none":[0, list()]}
	id_translate = {"2":"eubacteria", "2157":"archaea", "33208":"metazoans", "33090":"green_plants", "4751":"fungi", "none":"none"}
	
	nodes = get_nodes_objects(args.n)

	for study in species_dict:	
		#logmessage = "processing " + study
		#logging.info(logmessage)

		# trace back every species ID to (super)kingdom
		species_list = species_dict[study][1]
		species_count = species_dict[study][0]
		hits = 0
		for nid in species_list:
			if nid not in unique_species:
				unique_species.append(nid)
			while nid != "1":
				study = study.split("/")[-1]
				# check if targeted (super)kingdom taxon is found
				if (nid in kingdoms_table.keys()) and (study not in kingdoms_table[nid][1]):
					hits += 1
					kingdoms_table[nid][1].append(study)
				nid = nodes[nid].get_parentid()
		if hits == 0:
			study = study.split("/")[-1]
			kingdoms_table["none"][1].append(study)

	species_count = 0
	for nid in unique_species:
		species_count += 1
		while nid != "1":
			# check if targeted (super)kingdom taxon is found
			if nid in kingdoms_table.keys():
				kingdoms_table[nid][0] += species_count
				species_count = 0
			nid = nodes[nid].get_parentid()	
		kingdoms_table["none"][0] += species_count
		species_count = 0
	
	for kid in kingdoms_table:
		species_count = kingdoms_table[kid][0]
		studies_list = kingdoms_table[kid][1]
		print(id_translate[kid] + "\t" + str(species_count) + "\t" + str(len(studies_list)) 
			+ "\t" + str(studies_list).replace("'", "")[1:-1] )

	#log_file.close()

if __name__ == "__main__":
	main()