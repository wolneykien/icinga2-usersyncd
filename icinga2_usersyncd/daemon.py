# from importlib.resources import files
#

class Daemon:
    def __init__(self):
        pass

# from icinga2apic.client import Client
#
# client = Client(config_file='/etc/sysconfig/icinga2-apiusers-sync')
#
# client.objects.list('Host',
#                     filters='host.zone == zone',
#                     filter_vars={'zone': zone})
#
# types = ['ObjectCreated', 'ObjectDeleted']
# queue = queue
# filter = 'event.object_type == "Host"'
#
# for event in client.events.subscribe(types, queue, filter):
#     print(event)
#
#{"object_name":"test1","object_type":"Host","timestamp":1711707986.404245,"type":"ObjectCreated"}

## curl -k -sS -i -u 'root:bcf6ca38a4d66d17' -H 'Accept: application/json' -X POST 'https://localhost:5665/v1/events' -d '{ "queue": "abc", "types": ["ObjectCreated", "ObjectDeleted"], "filter": "event.object_type == \"Host\"" }'

#{"object_name":"test4","object_type":"Host","timestamp":1711708483.735119,"type":"ObjectCreated"}

#{"object_name":"test4","object_type":"Host","timestamp":1711708571.37147,"type":"ObjectDeleted"}
#{"object_name":"test3","object_type":"Host","timestamp":1711708583.605244,"type":"ObjectDeleted"}
#{"object_name":"test2","object_type":"Host","timestamp":1711708588.958552,"type":"ObjectDeleted"}
#{"object_name":"test1","object_type":"Host","timestamp":1711708592.050786,"type":"ObjectDeleted"}

#object ApiUser h {
#    client_cn = h
#    permissions = [{
#      permission = "actions/process-check-result"
#      filter = {{ host.name == h }}
#    }]
#  }

#actions/remove-acknowledgement

#icinga2 pki new-cert --cn icinga2-usersyncd --csr /tmp/icinga2-usersyncd.csr --key /tmp/icinga2-usersyncd.key --cert /tmp/icinga2-usersyncd.crt
#icinga2 pki sign-csr --cert /tmp/icinga2-usersyncd.crt --csr /tmp/icinga2-usersyncd.csr
