How to run the Make-based supertree pipeline
===========================================

The file [script/supertree/Makefile](https://github.com/aiblaauw/supertreebase/blob/master/script/supertree/Makefile) 
contains the steps for downloading TreeBASE data and preparing it for input into PAUP*. Below follows a discussion of
these steps, identified as make targets. 

If you want to work your way through these steps one by one, you would issue them in the order given, and you would do 
that inside the folder where the Makefile resides, i.e. in `script/supertree`. Most of the action will take place 
inside `data/treebase`. If you want to update the data with new studies, the sitemap.xml needs to be refreshed first before redoing the rest of the steps. For a completely fresh database dump you probably want to revert every step within the Makefile and then redo all of them; 

A number of steps can be parallelized by make, by providing the `-j $num` command to specify the number of cores to 
run on. To revert any steps, issue the target as `make <target>_clean` (example: `make sitemap_clean` deletes the
sitemap.xml):

Downloading and pre-processing
------------------------------

- `sitemap` - downloads the [sitemap.xml](http://treebase.org/treebase-web/sitemap.xml) from the TreeBASE website,
which lists all the studies currently published. The URLs are not pretty PURLs but URLs that directly compose the
query strings for the web application.
- `purls` - parses the sitemap.xml and extracts each URL, turning it into a PURL that points to the NeXML data
associated with the study. This means that inside `data/treebase` very many *.url files will be created: one for
each study. If a *.url file already exists it will be left alone, allowing for incremental downloads.
- `studies` - for every *.url file, downloads the NeXML file it points to. Again, this can be done incrementally
as make checks for the existence of target files (and their timestamps: if any *.url file is newer than a NeXML
file, a download is initiated, if the NeXML is newer than the URL, make assumes the target has been built and it
will leave well alone). _Some downloads fail (for a variety of reasons, e.g. the output is too much for
the web app to generate without timeouts). To get past this step you can create empty *.xml files, e.g. for 
study ID $foo, do `touch data/treebase/$foo.xml`_ Alternatively, it seems that NOT running this step parrallel and just recalling it when there was a timeout (or other problem that stopped the process), eventually collects as many downloads as possible.  
- `tb2mrp_taxa` - for each *.xml file, creates a *.txt file with multiple MRP matrices: one for each tree block in
the study. The *.txt file is tab separated, structured thusly: $treeBlockID, "\t", $ncbiTaxonID, "\t", $mrpString, "\n".
Note that at this point, $ncbiTaxonID can be anything: a (sub)species, genus, family, whatever.
- `taxa` - creates a file `taxa.txt` with two data columns: "\s+", $occurrenceCount, "\s+", $ncbiTaxonID, "\n"
- `species` - creates a file `species.txt` that maps the $ncbiTaxonID's to species IDs. The logic is as follows: if 
$ncbiTaxonID is below species level (e.g. subspecies), collapse up to species level. If $ncbiTaxonID is above species
level, expand it to include all the species _that are seen to be subtended by that taxon in any TreeBASE study_. So we
don't simply include all species in the NCBI taxonomy, just the ones TreeBASE knows about.
- `tb2mrp_species` - for each study MRP file (*.txt) maps the $ncbiTaxonID to the species ID. Results in a *.dat
file for every MRP *.txt file. _Note: the list of *.xml/*.txt/*.dat files is constructed by make from the list
of *.url files generated out of the sitemap. Other files with the *.txt extension (such as species.txt) are ignored.
- `ncbi` - downloads and extracts the NCBI taxonomy flat files into `data/taxdmp`
- `ncbimrp` - builds an MRP matrix for the species that occur in TreeBASE. _Note: this MRP matrix is not actually being
used further, so this target is a dead end for now._

Partitioning data 
------------------------------

if the normalized *.dat file for every MRP *.txt file was created, every datapoint (species) from every study can be mapped to the class rank it covers.

- `class_species` - creates a table file `class_species.txt` where every class is linked to the found species, with help of the NCBI taxnomy; class_ID \t species_count \t unique_species_count \t overlap percentage \t species_tax_ID,species_tax_ID,...
- `study_species` - creates a table file `study_species.txt` where every study is linked to the found species; study_ID \t species_count \t species_tax_ID,species_tax_ID,...
- `classes` - traces back every species id to class level with help of the NCBI taxonomy and the study_species.txt file, creating the following table `classes.txt`; class_name \t species_count \t study_count \t study_id_filename, study_id_filename, ...
- `partitions` - create MRP files for the found class ranks, containing the matrices for each found study. For example; Mammalia.mrp. This is done using classes.txt and class_species.txt
- `paup_nexus` - combines the MRP matrices to a large combined matrix, filling in the non-overlapping parts with questionmarks. The result is a Nexus file for every class-level partition. For example; Mammalia.nex -
the script is also creating a table for the class, mapping the study name to the amount of characters.
- `class_nchar` - makes the `class_nchar.txt` table (classname \t nchar), might be usefull in later calculations.

Analysis using PAUP* 
------------------------------

the MRP partitions will be converted into Nexus format to be used for analysis with the PAUP* program.

- `paupscript` - makes `bulk_exe.nex` in which the commands for the anaylsis of every Nexus file get collected  
- `class_trees` - infering trees for every class partition (*.tre), using the heuristic method in PAUP* (using the commands described in the `spr_inference.nex` script)
- `pauplog_table` - parsing the logfile that resulted from all the PAUP* runs, so that class names get linked to their scores (class_name \t min_steps \t steps \t CI \t RI \t RC \t goloboff_fit), found in `class_scores.txt`  

Visualization 
------------------------------

For visualization, there are separate scripts collected in [script/visualization/Makefile](https://github.com/aiblaauw/supertreebase/blob/master/script/visualization/Makefile), containing the following targets.


- `mrp_bipartition` - calculates bipartition (*.mrpsplit) for every *.mrp class, giving the following table output, separated by study_id labels: charnum \t ingroup_leaf,ingroup_leaf,.. \t outgroup_leaf,outgroup_leaf,.. 
- `tree_bipartition` - comparing the splits to the splits found in every *.tre file, with help of the *mrpsplit files, it decides a scoring for every node in the Class tree in a *.treesplit file: node_id \t study_id_match,study_id_match,.. \t study_id_oppose,study_id,oppose,.. \t (match_count/oppose_count)/total_count 
- `csvtrees` - taking the Newick trees and convert them into csv format (child /t parent) which makes it easier to read for visualization and makes it possible to add metadata 
- `htmltrees` - adding the csvtree into a html file for visualization, with help of the D3.js library

Collect metadata 
------------------------------

also the metadata behind the original databse entries will be collected,
for this, the Make targets within [script/characters/Makefile](https://github.com/aiblaauw/supertreebase/blob/master/script/characters/Makefile) can be used!! Ouput will be collected in `metadata/characters`.

- `meta` - creates *.meta files for every study, describing publication date, matrix info (data source type, nchar, ntax) and tree info (ntax, quality label, type and kind of tree assambled)
- `metaextract` - this reduces the *.meta files to a `metaextract.txt`, a table linking study ID's to the relevant metadata (study_ID \t year \t datatype)  
- `allmeta` - combining the text from every *.meta file to one file named `meta.tsv`
- `metasummary` - using the combined text, creates `metasummary.txt` to show some percentages, describing the distribution of the (meta)data types
