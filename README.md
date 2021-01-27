# python-cron made by Daniil Tovstolug
you must have config file config.ini. It`s structure:

crontab_path = <path to crontab file> 
logging_config = <path to logger config file>
logger_name = <logger name which will be used>

most important fiedls in logger config file:
loger level and hadler level should be equal
path to logs indicated in the first parameter of handler args
logging format indicated in format of formatter