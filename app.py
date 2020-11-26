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


def log_info(message, path):
    
    file = open(path,'a')
    file.write(f'Info: [{datetime.utcnow()} UTC]: {message}\n')
    file.close()
    
        
def log_error(message, path):
    
    file = open(path,'a')
    file.write(f'Error: [{datetime.utcnow()} UTC]: {message}\n')
    file.close()


def is_same_datetime(date):
    return date == get_date_dict()


def get_date_dict():
    return {'hours':datetime.now().hour,
        'minutes': datetime.now().minute,
        'day':datetime.now().day,
        'month':datetime.now().month}


def run_cron():

    configs = get_configs()
    cron = CronTab(tabfile=configs['crontab_path'])

    while True:
        
        date = get_date_dict()
        
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
                        log_info(f'Command: {command}', configs['logs_path'])
                        os._exit(pid)

            except Exception as e:
                log_error(f'{str(e)}. Command: {command}', configs['logs_path'])
        
        sleep_time = (60 - datetime.now().second)/5
        
        while is_same_datetime(date):
            time.sleep(sleep_time)
        


if __name__ == "__main__":
    run_cron()
