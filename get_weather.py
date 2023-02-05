from pyowm import owm
import sys
try:
	import conf
except:
	sys.stderr.write("ERR: conf.py not found")
	sys.exit(1)
owm = owm.OWM(conf.owm_api_key)

mgr = owm.weather_manager()
observation = mgr.weather_at_place('Binghamton,US').weather

condition = observation.detailed_status
print(condition)
