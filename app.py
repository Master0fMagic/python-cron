from crontab import CronTab
from croniter import croniter
from datetime import datetime, timedelta
import subprocess
import os
import signal
import configparser
import logging, logging.config

config_file = 'config.ini'
logger = None
config = None

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
            logger.debug(f'job object was added to list: {str(job_objects[-1])}')
    except Exception as ex:
        logger.error(f'Error was caught: {ex}')

    logger.info(f'job_objects list was created. It`s length: {len(job_objects)}')
    return job_objects


def create_default_config(config):
    config['DEFAULT'] = {'crontab_path': 'crontab',
                    'logger_config': 'logger_config.conf',
                    'logger_name': 'logger'}
    with open(config_file, 'w') as configfile:
        config.write(configfile)


def setup():    
    global config
    config =  configparser.ConfigParser(interpolation=None)
    if not os.path.exists(config_file):
        create_default_config(config)
    config.read(config_file)
    
    if not os.path.exists(config['DEFAULT']['active_session_file']):
        with open(config['DEFAULT']['active_session_file'],'w') as file:
            file.write(str(os.getpid()))
    with open(config['DEFAULT']['active_session_file'],'r') as file:
        running_cron_pid = file.readline()
        if running_cron_pid != '':
            try:
                os.kill(int(running_cron_pid),signal.SIGTERM)
            except Exception:
                file.close()
    with open(config['DEFAULT']['active_session_file'],'w') as file:
        file.write(str(os.getpid()))

    if not os.path.exists(config['DEFAULT']['logger_config']):
        print('Error. Logger configs not found')
        os._exit(1)
    
    logging.config.fileConfig(fname=config['DEFAULT']['logger_config'], disable_existing_loggers=False)
    global logger
    logger = logging.getLogger(config['DEFAULT']['logger_name'])

    if not os.path.exists(config['DEFAULT']['CRONTAB_PATH']):
        logger.critical('Crontab file was not found at %s'%config['DEFAULT']['CRONTAB_PATH'])
        os._exit(1)

    cron = CronTab(tabfile=config['DEFAULT']['CRONTAB_PATH'])
    
    logger.info('crontab was read successfully')
    job_objects = get_job_objects(cron)
    return job_objects


def run_cron(job_objects):

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
                    logger.info(f'Command {job["command"]} was executed')
                    os.kill(os.getpid(), signal.SIGTERM)
                    
            for child in childrens:
                os.waitpid(child,0)
            childrens = list()

        except Exception as ex:
            logger.error(f'Exception were caught: {ex}')


if __name__ == "__main__":
    try:
        job_objects = setup()
        logger.info('Cron start running...')
        run_cron(job_objects)
    except Exception as ex:
        print(ex)
        if logger != None:
            logger.critical(f'Error was caugth: {ex}')
        os.kill(os.getpid(), signal.SIGTERM)
