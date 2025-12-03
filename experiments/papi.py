from pypapi import papi_low as papi
from pypapi import events

papi.library_init()

evs = papi.create_eventset()
papi.add_event(evs, events.PAPI_TOT_CYC)

papi.start(evs)

# Do some computation here
start = 0.0
for i in range(100_000):
    start += i

result = papi.stop(evs)
print(result)

papi.cleanup_eventset(evs)
papi.destroy_eventset(evs)
