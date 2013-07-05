import logging
import os
#---- Custom modules
from organizers import Configuration     #Used to read JSON/XML configuration files.

#[] Global Configuration Variables
_config = Configuration.read("settings.json")

#LOG LEVELS: - these are stacked ~~> 'level' in .basicConfig sets a threshold for recording
#DEBUG    Detailed information, typically of interest only when diagnosing problems.
#    logging.debug('Message here, with variables %s and %s',var1,var2)
#INFO    Confirmation that things are working as expected.
#    logging.info()       #normal execution
#WARNING    An indiction that something unexpected happened, or indicative of some problem in the near future (eg 'disk space low'). The software is still working as espected.
#    logging.warning()    #indicitive of some problem, but software working
#ERROR    Due to a more serious problem, the software has not been able to perform some function.
#    logging.error()      #more serious problem - software has been unable to preform some function
#EXCEPTION    Similar to error, but dumps stack. Call only from a try: catch: block.
#    logging.exception()  #includes a stack trace
#CRITICAL    A serious error, indicating that the program itself may be unable to continue running.
#    logging.critical()   #A serious error, indicating that the program itself may be unable to continue running


def setup_error_log():
    images_log_file = _config['logs']['dir']+_config['logs']['error']
    if not os.path.exists( images_log_file):
        with open(images_log_file,'w') as lg:
            pass
    logging.basicConfig(filename=images_log_file,
                format='%(levelname)s: %(filename)s-%(funcName): %(asctime)s: %(message)s',
                datefmt='%m/%d/%Y %I:%M:%S %p',
                level=logging.DEBUG)
