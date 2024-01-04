<h1>WAYBACK SEARCH TOOL</h1>

Example: `python3 wb_search.py --d www.domain.com --sref wb_search_patterns.txt --sf wb_search_strings.txt --more_print 50 --y 2023 --eachDay true --m 10 --saveRes "/tmp/WB_DB" --verbose true`

```
Usage: python3 wb_search.py [-h] [--d D] [--file FILE] [--s S] [--sf SF] [--sre SRE] [--sref SREF] [--more_print MORE_PRINT] [--y Y] [--m M] [--extract EXTRACT] [--eachMonth EACHMONTH] [--eachDay EACHDAY] [--output OUTPUT] [--saveRes SAVERES] [--verbose VERBOSE]
                    [--proxy PROXY] [--example EXAMPLE]

Optional arguments:
  -h, --help            show this help message and exit
  --d D                 Domain needed to wayback
  --file FILE           --file /path_to_file/domains.txt
  --s S                 Find this string in respond of each records
  --sf SF               Path to file of strings to find respond of each records
  --sre SRE             Find regex pattern in respond of each records
  --sref SREF           Path to file of regex patterns to find respond of each records
  --more_print MORE_PRINT
                        Get more nums of character after found string, default is 20
  --y Y                 Do wayback for this year, blank for all years
  --m M                 Do wayback for this month, blank for all years
  --extract EXTRACT     Extract found wayback url. Example: "--extract true" (default is None)
  --eachMonth EACHMONTH
                        Only get 1 snapshot in each months. Example: "--eachMonth true" (default is None)
  --eachDay EACHDAY     Only get 1 snapshot in each days. Example: "--eachDay true" (default is None)
  --output OUTPUT       Path to directory to save result file
  --saveRes SAVERES     Path to directory to save responses
  --verbose VERBOSE     Verbose
  --proxy PROXY         --proxy http://127.0.0.1:8080
```
