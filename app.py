from crontab import CronTab
from croniter import croniter
from datetime import datetime, timedelta
import subprocess
import os
import config
import signal


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



def get_job_objects(cron):
    '''returns a list of {schedule, next_execute_time, command} objects
    schedule is a croniter object
    next_execute_time - datetime object which stores when should a job be executed next time
    command - command to execute'''
    job_objects = list()
    time = datetime.now() - timedelta(minutes = 1)
    try:
        for cron_row in cron:
            schedule_row = cron_row.schedule(date_from = time)
            job_objects.append({'schedule':schedule_row, 'next_execute_time':schedule_row.get_next(), 'command':cron_row.command})
    except Exception as ex:
        #log error
        print(ex)
    #log info
    return job_objects


def setup():
    if not os.path.exists('logs'):
        os.mkdir('logs')
    configs = get_configs()
    cron = CronTab(tabfile=configs['crontab_path'])
    job_objects = get_job_objects(cron)
    return job_objects


def run_cron():
    job_objects = setup()
        
    childrens = list()
    
    while True:
        try:
            current_time = datetime.now()
            for job in job_objects:
                if job['next_execute_time'] <= current_time:
                    job['next_execute_time'] = job['schedule'].get_next()
                    pid = os.fork()
                    if pid != 0:
                        childrens.append(pid)
                        continue
                    subprocess.run(job['command'], shell=True)
                    os.kill(os.getpid(), signal.SIGTERM)
                    #log info
            for child in childrens:
                os.waitpid(child,0)
            childrens = list()

        except Exception as ex:
            print(ex)
            #log error
  

if __name__ == "__main__":
    try:
        run_cron()
    except Exception as ex:
        print(ex)
        #log error
        os.kill(os.getpid(), signal.SIGTERM)
