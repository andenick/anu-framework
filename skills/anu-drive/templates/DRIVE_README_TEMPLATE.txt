================================================================
  <<PROJECT_TITLE>>
  Data Package -- Version <<VERSION>>
  <<DATE>>
================================================================


WHAT IS THIS?
-------------
This folder contains <<N_SERIES>> constructed economic data
series covering <<YEAR_START>> to <<YEAR_END>>, based on the
empirical work in:

  <<ORIGINAL_AUTHOR>>
  "<<ORIGINAL_TITLE>>" (<<ORIGINAL_YEAR>>)
  <<PUBLISHER>>

The data has been replicated from the original source
material and extended to the present using publicly
available government statistical APIs (<<API_LIST>>).


HOW TO USE THIS DATA
--------------------

  1. QUICK START -- All data in one file:

     Open "<<MASTER_XLSX>>"

     Row 1 = Series names (human-readable)
     Row 2 = Series IDs (S001, S002, ...)
     Row 3 = Units of measurement
     Row 4 onward = Data (Year in first column)

  2. DEEP DIVE -- Full construction of any series:

     Open the "Series/" folder.
     Each file shows one data series with:
       - Sheet 1 (Data): Every raw input and transformation
       - Sheet 2 (Provenance): Where every number came from
       - Sheet 3 (Research): Original author's methodology
       - Sheet 4 (Construction): Step-by-step build log

  3. FULL METHODOLOGY:

     Open "<<METHODOLOGY_PDF>>"
     The Table of Contents has clickable links to every
     series. Click any series ID to jump to its full
     documentation: definition, inputs, construction
     process, and output description.

  4. PROGRAMMATIC USE (R, Python, Stata):

     Import "<<MASTER_CSV>>" directly.
     See Appendix C of the Methodology PDF for
     language-specific import code.

  5. VARIABLE REFERENCE:

     Open "<<CODEBOOK_CSV>>"
     One row per series with: ID, name, definition,
     units, coverage, source, and more.

  6. CITING THIS DATA:

     See CITATION.txt for a formatted citation
     and BibTeX entry. Please also cite the
     original work by <<ORIGINAL_AUTHOR>>.


SERIES LIST
-----------
<<SERIES_LIST>>


CONTENTS
--------
<<MASTER_XLSX>>            All series (Excel)
<<MASTER_CSV>>             All series (CSV)
<<CODEBOOK_CSV>>           Data dictionary
<<METHODOLOGY_PDF>>        Full methodology
CITATION.txt               How to cite this data
Series/                    Individual series workbooks
<<SERIES_FILE_LIST>>
README.txt                 This file


DATA SOURCES
------------
<<DATA_SOURCES_SUMMARY>>


CONTACT
-------
<<AUTHOR_NAME>>
<<INSTITUTION>>
<<EMAIL>>


LICENSE
-------
<<LICENSE_TEXT>>


================================================================
  Generated <<DATE>> by the Anu Framework
  https://github.com/<<REPO_URL>>
================================================================
