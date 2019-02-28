# WordCounts

This is a simple script that will send you an email with the total number of words you wrote in a given file or filepath. By setting it up with a crontab, you can get daily emails with the number of words you wrote. 

## Installation

1. Clone the repository:
	```
	git clone https://github.com/marcosfelt/wordcount.git
	```

2. Change wordcount_config.json to have your email and desired filepaths.

3. Sign up for a [sendgrid account](https://signup.sendgrid.com/) and store your API key in a .env file under the name 'SENGRID_API_KEY'

4. Add the job to your crontab

	```env EDITOR=vim crontab -e```

	```55 23 cd /path/to/this/repository && pipenv run wordcounts.py```

This will now send you an email at 11:55 PM every night with the number of words you wrote that day!
