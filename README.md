VT Hunter Configuration
-----------------------

1. Copy etc/vt_example.ini to etc/vt.ini. Open etc/vt.ini and modify as necessary.
2. Copy etc/logging_example.ini to etc/logging.ini. Open etc/logging.ini and modify as necessary.
3. Configure fetchmail to use the fetchmail_processor.py script.
	a) copy fetchmailrc-example to ~/.fetchmailrc
	b) modify ~/.fetchmailrc to include your information
		* You might need to run fetchmail -B 1 -v to find the new SSL fingerprint of the email server and put that in fetchmailrc
4. Copy campaign_translation_example.db to campaign_translation.db. Modify as necessary. See campaign translation section for details.
5. Copy vtmis/scoring_example.py to vtmis/scoring.py. Modify vtmis/scoring.py to include weights for your custom campaigns.
6. The database will be created the first time you run anything that uses it.

## Dependencies
* sqlalchemy
* requests
* configparser

You may want to use a virtual environment to install your dependencies. You can use pyvenv to set this up.

## Campaign Translation
campaign_translation.db contains mappings to do string substitution on campaign names. You might use this if you don't want to put your internal campaign names on VirusTotal in any form (such as a yara rule name). This will allow you to provide an "external_name" (the fake name), which will then be converted to the "internal_name" when the data is processed.

As a further example. Our internal name for a specific campaign is "Mighty Bear". We want to track this campaign name in a yara rule on VT, so we create a fake name called "campaign1". Our rule is then named "rule prod_campaign1_pivy_strings". We also create a campaign_translation.db entry as so:

```
{
    "campaign1" : "mightybear",
}
```

Now when we receive alerts and the emails are processed, this substitution will occur.

One last note. Unless you have a specific reason (such as some tagging scheme), it is probably a good idea to remove underscores from your campaign names. Underscores are used internally to separate rule names into tags. This might split your campaign name into two or more separate tags you don't want.

## Scoring
scoring.py can be implemented in any way you see fit. The default implementation takes tags for the VT yara hit (based on the yara rule name) and assigns points based on the keywords found. Certain campaigns can be assigned a greater weight, while there is also room for keywords based on specific malware or other special keywords you can define. The result is computed and returned via the get_string_score(rule) function.

## The Process
1. Run fetchmail. The -B option lets you limit the number of emails. This is also intended to be placed in a cron job.
2. Process the emails with email_to_db.py
3. Review alerts with review_alerts.py
4. Download and submit samples to your analysis module with process_downloads.py

NOTE: When running in crontab, you need to cd to the vt-hunter directory first. Like so:
```
*/15 * * * *    cd /path/to/vt-hunter && /usr/bin/fetchmail >> /path/to/log/fetchmail.log
```

## Automation
Currently, automation occurs via crontab. You want to automate the following tasks:
* fetchmail
* email_to_db.py

You will also want to run the following in a screen session:
* process_downloads.py

At some point, the functionality of email_to_db.py can be moved to fetchmail_processor.py. I just haven't done this yet.

## Analysis Modules
process_downloads.py is capable of submitting downloaded samples to any automated analysis you might have. To do so, create an analysis module in the analysis/ directory. You must do the following:
* Create your_analysis_module.py in analysis/
** Implement the methods in analysis.py
* Add your_analysis_module to analysis/__init__.py
* Add your_analysis_module section to local_settings.ini

For example, if your_analysis_module looked like the following:

```
import analysis

class YourAnalysisModule(analysis.AnalysisModule):

    def analyze_sample(self, filename='', tags=[]):
        # Do any analysis steps you want here. This could launch an external
	# script or be entirely self contained.
	print('Opening file: ' + filename)

    def check_status(self, filename=''):
	# This determines when a file has completed analysis. If you don't
	# want to deal with this, just return True
	print('Analysis completed.')
	return True
```

You would then add the following section to local_settings.ini:

```
[analysis_module_your_analysis_module]
module = analysis.your_analysis_module
class = YourAnalysisModule 
enabled = yes
```

Notice the "your_analysis_module" parts are the exact same as your_analysis_module.py. This convention is important to follow.

## Optional malware selection process
* TODO: Configure "no review", aka direct download from email hits. Based on keywords from the rule name perhaps?
