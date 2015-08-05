import analysis
from subprocess import Popen
import os

class MWZoo(analysis.AnalysisModule):

    '''
    This submits the sample to our malware zoo for analysis. We use an external
    process for this submission.
    '''
    def analyze_sample(self, filename='', tags=[]):
        # When we submit the sample to the mwzoo, it will create a copy of that sample
        # in its directory structure.
        formatted_tags = []
        for tag in tags:
            formatted_tags.append('-t')
            formatted_tags.append(tag)

        subdir = ''
        if len(tags) > 0:
            subdir = "_".join(sorted(tags))
        # The data directory for the file
        mwzoo_dirname = '/opt/mwzoo/data/vt/' + subdir

        '''
        For reference, here is the add-sample command for our mwzoo:
        usage: add-sample [-h] [--enable-download] -t TAGS -s SOURCE
                          [--comment COMMENT] [-d SUBDIRECTORY] [--disable-analysis]
                          input_data [input_data ...]

        Add a given file or download by hash from VirusTotal.

        positional arguments:
          input_data            The files or hashes or add. Accepts file paths and
                                                                      md5, sha1 and/or sha256 hashes.

        optional arguments:
          -h, --help            show this help message and exit
          --enable-download     Enable downloading files from VirusTotal.
          -t TAGS, --tags TAGS  Add the given tag to the sample. Multiple -t options
                                are allowed.
          -s SOURCE, --source SOURCE
                                Record the original source of the file.
          --comment COMMENT     Record a comment about the sample.
          -d SUBDIRECTORY, --subdirectory SUBDIRECTORY
                                File the sample in the given subdirectory. Defaults to
                                processing the file where it's at.
          --disable-analysis    Do not analyze files, just add them.
        '''
        Popen( ['/opt/mwzoo/bin/add-sample', '-s', 'vt', '--comment', 'VirusTotal automated download'] + formatted_tags + [ '-d', mwzoo_dirname, filename ] )

        # Then we need to call the analyze function for the mwzoo. We should have a
        # configuration option that specifies whether to run the sample through
        # a sandbox or not.
        Popen( ['/opt/mwzoo/bin/analyze', '-d', 'cuckoo', mwzoo_dirname + "/" + os.path.basename(filename)] )

    def check_status(self, filename='', tags=[]):
        subdir = ''
        if len(tags) > 0:
            subdir = "_".join(sorted(tags))
        # The data directory for the file
        mwzoo_dirname = '/opt/mwzoo/data/vt/' + subdir
        # If the name.running file is present the analysis is still running.
        if os.path.isfile(mwzoo_dirname + os.path.basename(filename) + '.running'):
            # Still running
            return False

        # Analysis complete!
        print('Analysis complete for {0}'.format(filename))
        return True

    # Called at the end of the processing.
    def cleanup(self, filename='', tags=[]):
        # Remove the malware file
        print("Removing {0}".format(filename))
        os.remove(filename)
