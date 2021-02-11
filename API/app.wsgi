import sys
sys.path.insert(0, '/var/www/FSDF-Powerlines/API/power_lines')
sys.path.insert(0, '/var/www/FSDF-Powerlines/API/power_stations')
sys.path.insert(0, '/var/www/FSDF-Powerlines/API/power_substations')
sys.path.insert(0, '/var/www/FSDF-Powerlines/API')

from app import app as application
