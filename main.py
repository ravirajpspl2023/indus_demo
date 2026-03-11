import logging
from module.humac_driver import humac_driver
import time

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s | %(levelname)s| %(name)s | %(message)s',
                    datefmt='%H:%M:%S',handlers=[ logging.StreamHandler()])

def main():
    logging.info("HUMAC DRIVER STARTED ...")
    time.sleep(10)
    humac = humac_driver()
    humac.start() 
    logging.info("HUMAC DRIVER STOPPED ...")
if __name__ == "__main__":
    main()