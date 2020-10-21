from crontab import CronTab
from croniter import croniter
from datetime import datetime
import subprocess
import os
import time
import config


def get_configs():
    
    configs = {}
    
    if config.CRONTAB_PATH == '' :
        configs['crontab_path'] = config.DEFAULT_CRONTAB_PATH
    
    else:
        configs['crontab_path'] = config.CRONTAB_PATH
    
    if config.LOGS_PATH == '':
        configs['logs_path']= config.DEFAULT_LOGS_PATH
    
    else: 
        configs['logs_path'] = config.LOGS_PATH
    
    return configs


def run_cron():

    configs = get_configs()
    cron = CronTab(tabfile=configs['crontab_path'])

    while True:
        for i in range(len(cron)):
            format = str(cron[i]).split(' ')
            if format[0] == '#':
                continue

            command_time = ''.join(s + ' ' for s in format[0:5] ).strip()
            command = ''.join(s + ' ' for s in format[5:]).strip()
            
            try:
                if croniter.match(command_time, datetime.now()):
                    pid = os.fork() 
                    if pid == 0:
                        continue
                    else:
                        subprocess.run(command, shell=True)
                        os._exit(pid)

            except Exception as e:
                file = open(configs['logs_path'],'a')
                file.write(f'[{datetime.now()}]: {str(e)}\n')
                file.close()

        time.sleep(60 - datetime.now().second)


if __name__ == "__main__":
    run_cron()
