# this makefile contains the steps needed for running a supertree analysis

# eukaryotes
ROOTID=2759

# runtime verbosity
VERBOSITY=-v -v -v
ARCH=zip

# relative locations. it is possible that these relative paths won't work when recursive
# make is invoked from a different working directory
SCRIPT=.
DATA=../../data

# contained folders. these are based on the relative locations defined above and probably
# don't need to be updated, ever
MRPDIR=$(DATA)/mrp
TAXDMP=taxdmp
TAXDMPDIR=$(DATA)/$(TAXDMP)
TAXDMPTMP=$(TAXDMPDIR)/tmp
TB2DATA=$(DATA)/treebase

# standard commands. unless these commands are installed in a non-standard location (this should be
# very rare) there is no need to change these
PERL=perl
PYTHON=python3
EXTRACT=unzip
MKPATH=mkdir -p
RM_RF=rm -rf
CURL=curl
WGET=wget
CAT=cat
ECHO=echo
FIND=find
CHMOD=chmod
PAUP=/home/ubuntu/Downloads/paup4a154_ubuntu64/paup4a154_ubuntu64

# file locations. these are based on contained folders defined above and probably
# don't need updating, ever
MRPTABLE=$(MRPDIR)/combined.dat
TAXDMPARCH=$(TAXDMPDIR)/$(TAXDMP).$(ARCH)
NCBIMRP=$(MRPDIR)/ncbi.dat
NCBICON=$(MRPDIR)/ncbi_constraints.tnt
NCBINODES=$(TAXDMPDIR)/nodes.dmp
NCBINAMES=$(TAXDMPDIR)/names.dmp
TB2SITEMAP=sitemap.xml
TB2SITEMAPXML=$(TB2DATA)/$(TB2SITEMAP)
TB2TAXA=$(TB2DATA)/taxa.txt
#TB2LINEAGES=$(TB2DATA)/lineages.txt
TB2SPECIES=$(TB2DATA)/species.txt
TB2STUDYSPECIES=$(TB2DATA)/study_species.txt
TB2CLASSSPECIES=$(TB2DATA)/class_species.txt
TB2CLASS=$(TB2DATA)/classes.txt
#TB2NCHAR=$(TB2DATA)/nchar.txt

PAUPSCRIPT=$(TB2DATA)/bulk_exe.nex
PAUPANALYSIS=$(TB2DATA)/spr_analysis.nex
PAUPLOG=$(TB2DATA)/paup_log.txt
PAUPLOGTABLE=$(TB2DATA)/class_scores.txt
CLASSNCHAR=$(TB2DATA)/class_nchar.txt

# URLs. these are based on variables defined above and probably don't need updating, ever
TAXDMPURL=ftp.ncbi.nlm.nih.gov/pub/taxonomy/$(TAXDMP).$(ARCH)
TB2SITEMAPURL=http://treebase.org/treebase-web/$(TB2SITEMAP)

# file lists.
NCBIFILES=$(NCBINODES) $(NCBINAMES)
TB2STUDYPURLS=$(wildcard $(TB2DATA)/*.url)
TB2STUDYFILES=$(patsubst %.url,%.xml,$(TB2STUDYPURLS))
TB2MRPFILES=$(patsubst %.xml,%.txt,$(TB2STUDYFILES))
TB2NRMLMRP=$(patsubst %.xml,%.dat,$(TB2STUDYFILES))

TB2CLASSES=$(patsubst %.xml,%.class,$(TB2STUDYFILES))
PARTITIONS=$(wildcard $(TB2DATA)/*.mrp)
PAUPNEXUS=$(patsubst %.mrp,%.nex,$(PARTITIONS))
CHARLABELS=$(wildcard $(TB2DATA)/*_charlabels.txt)
#VALIDNEXUS=$(wildcard $(TB2DATA)/*.nex)
CLASSTREES=$(patsubst %.nex,%.tre,$(PAUPNEXUS))


.PHONY : 


# fetch the TreeBASE site map
$(TB2SITEMAPXML) :
	$(MKPATH) $(TB2DATA)
	$(RM_RF) $(TB2SITEMAPXML)
	$(WGET) -O $(TB2SITEMAPXML) $(TB2SITEMAPURL)
sitemap : $(TB2SITEMAPXML)
sitemap_clean : 
	$(RM_RF) $(TB2SITEMAPXML)

# turn the study URLs in the site map into local *.url files with PURLs
purls : $(TB2SITEMAPXML)
	$(PERL) $(SCRIPT)/make_tb2_urls.pl -i $(TB2SITEMAPXML) -o $(TB2DATA)
purls_clean : 
	$(RM_RF) $(TB2DATA)/%.url

# fetch the studies
$(TB2STUDYFILES) : %.xml : %.url
	$(CURL) -L -o $@ `cat $<`
studies : $(TB2STUDYFILES)
studies_clean : 
	$(RM_RF) $(TB2STUDYFILES)

# make TreeBASE MRP matrices
$(TB2MRPFILES) : %.txt : %.xml
	$(PERL) $(SCRIPT)/make_tb2_mrp.pl -i $< $(VERBOSITY) > $@
tb2mrp_taxa : $(TB2MRPFILES)
tb2mrp_taxa_clean : 
	$(RM_RF) $(TB2MRPFILES)

# create list of unique taxon IDs with occurrence counts
$(TB2TAXA) : $(TB2MRPFILES)
	cat $(TB2MRPFILES) | cut -f 2 | sort | uniq -c > $@
taxa : $(TB2TAXA)
taxa_clean : 
	$(RM_RF) $(TB2TAXA)

# make species-level list from TreeBASE taxon IDs
$(TB2SPECIES) : $(TB2TAXA) $(NCBIFILES)
	$(MKPATH) $(TAXDMPTMP)
	$(PERL) $(SCRIPT)/make_species_list.pl -taxa `pwd`/$(TB2TAXA) -nodes `pwd`/$(NCBINODES) -names `pwd`/$(NCBINAMES) -dir `pwd`/$(TAXDMPTMP) $(VERBOSITY) > $@
species : $(TB2SPECIES)
species_clean : 
	$(RM_RF) $(TB2SPECIES)

# make MRP tables with normalized species and ambiguity codes for polyphyly
$(TB2NRMLMRP) : %.dat : %.txt
	$(PERL) $(SCRIPT)/normalize_tb2_mrp.pl -i $< -s $(TB2SPECIES) $(VERBOSITY) > $@
tb2mrp_species : $(TB2NRMLMRP)
tb2mrp_species_clean : 
	$(RM_RF) $(TB2NRMLMRP)
 

# download taxdmp archive
$(NCBIFILES) :
	$(MKPATH) $(TAXDMPDIR)
	$(CURL) -o $(TAXDMPARCH) $(TAXDMPURL)
	cd $(TAXDMPDIR) && $(EXTRACT) $(TAXDMP).$(ARCH) && cd -
ncbi : $(NCBIFILES)
ncbi_clean : 
	$(RM_RF) $(TAXDMPDIR)

# make NCBI MRP matrix
$(NCBIMRP) : $(NCBIFILES) $(TB2SPECIES)
	$(MKPATH) $(MRPDIR) $(TAXDMPTMP)
	$(PERL) $(SCRIPT)/make_ncbi_mrp.pl -species $(TB2SPECIES) -nodes $(NCBINODES) -names $(NCBINAMES) -dir $(TAXDMPTMP) $(VERBOSITY) > $@
ncbimrp : $(NCBIMRP)
ncbimrp_clean : 
	$(RM_RF) $(NCBIMRP)


### Partitioning ### 

# making table showing species ID's linked to class ID's

$(TB2CLASSSPECIES) : $(TB2NRMLMRP) $(NCBIFILES)
	$(PYTHON) $(SCRIPT)/class_species.py -i $(TB2DATA)/ -t `pwd`/$(NCBINODES) -n `pwd`/$(NCBINAMES) >> $@
class_species : $(TB2CLASSSPECIES)
class_species_clean:
	$(RM_RF) $(TB2CLASSSPECIES)
 
# making a table showing species ID's within every study
$(TB2STUDYSPECIES) : $(TB2NRMLMRP) 
	for f in $(TB2NRMLMRP) ; do \
		$(PYTHON) $(SCRIPT)/study_species.py -i $$f >> $@ ; \
   done
study_species : $(TB2STUDYSPECIES)
study_species_clean:
	$(RM_RF) $(TB2STUDYSPECIES) 
 
# find class levels found in every study
$(TB2CLASS) : $(TB2STUDYSPECIES) $(NCBIFILES)
	$(PYTHON) $(SCRIPT)/make_classes.py -i $< -t `pwd`/$(NCBINODES) -n `pwd`/$(NCBINAMES) -o $@
classes : $(TB2CLASS)
classes_clean:
	$(RM_RF) $(TB2CLASS)
 
# create a file with a list of corresponding MRP matrices, for each taxonomic class 
partitions: $(TB2CLASSSPECIES) $(TB2CLASS)
	$(PYTHON) $(SCRIPT)/make_partitions_mrp.py -c $(TB2CLASSSPECIES) -s $(TB2CLASS) -n `pwd`/$(NCBINAMES)
partitions_clean:
	- $(RM_RF) $(TB2DATA)/*.mrp
   
# create NEXUS files with large combined MRP matrices
$(PAUPNEXUS) : %.nex : %.mrp
	$(PYTHON) $(SCRIPT)/combine_mrp.py -i $< >> $@
paup_nexus : $(PAUPNEXUS)
paup_nexus_clean : 
	$(RM_RF) $(PAUPNEXUS)
	$(RM_RF) $(CHARLABELS)
 
# make a table that links Class-names to the number of characters used
$(CLASSNCHAR) : $(PAUPNEXUS)
	$(PYTHON) $(SCRIPT)/get_nchar.py >> $@
class_nchar : $(CLASSNCHAR)
class_nchar_clean : 
	$(RM_RF) $(CLASSNCHAR)


### PAUP* method ###
 
# make NEXUS file with PAUP* commands
$(PAUPSCRIPT) : $(PAUPNEXUS)
	$(PYTHON) $(SCRIPT)/combine_paupscript.py >> $@
paupscript : $(PAUPSCRIPT)
paupscript_clean : 
	$(RM_RF) $(PAUPSCRIPT)
 
# create Newick tree files for every class
$(CLASSTREES) : $(PAUPSCRIPT)
	$(PAUP) $<
class_trees : $(CLASSTREES)
class_trees_clean : 
	$(RM_RF) $(CLASSTREES)
	$(RM_RF) $(PAUPLOG) 
 
# parse the PAUP* logfile
$(PAUPLOGTABLE) : $(PAUPLOG)
	$(PYTHON) $(SCRIPT)/parse_pauplog.py -i $< >> $@
pauplog_table : $(PAUPLOGTABLE)
pauplog_table_clean : 
	$(RM_RF) $(PAUPLOGTABLE)