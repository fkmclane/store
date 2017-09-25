# address to listen on
addr = ('', 8080)

# directory to store information
dir = '/var/lib/store'

# log locations
log = '/var/log/store/store.log'
http_log = '/var/log/store/http.log'

# template directory to use
import os.path
template = os.path.dirname(__file__) + '/html'

# minute of hour to prune files
minute = 9

# number of random characters to use
random = 6
