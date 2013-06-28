import random
import re
import requests
import string
import sys
import time


tags = ['GET', 'POST', 'PUT']
scenario_steps = []
registry = {}


def do_request(step):
    method = step[0]
    repeat = int(step[1])
    url, data = get_url(step[2:])
    if method == 'GET':
        for i in range(0, repeat):
            process_response(requests.get(url))
    elif method == 'POST':
        for i in range(0, repeat):
            process_response(requests.post(url, data=data))
    elif method == 'PUT':
        for i in range(0, repeat):
            process_response(requests.put(url, data=data))
    else:
        raise Exception('Unsupported method: %s' % method)


def get_url(fields):
    """Construct the url by replacing {var} with values
    append server address, process payload data for POST,
    PUT.
     """
    partial_url = fields[0].strip()
    vars_ = re.findall('\{(\w+)\}', partial_url)
    for var in vars_:
        pattern = '\{%s\}' % var
        partial_url = re.sub(pattern, str(registry[var]), partial_url)

    url = registry['server'] + partial_url

    # payload data for POST, PUT
    data = {}
    for field in fields[1:]:
        kv = field.strip().split('=')
        key = kv[0]
        val = kv[1]
        is_rvar = re.findall('\{(\w+)\}', val)
        if is_rvar:
            if is_rvar[0] == 'rint':
                val = randomint()
            elif is_rvar[0] == 'print':
                try:
                    val = registry['print']
                except KeyError:
                    registry['print'] = val = randomint()

            elif is_rvar[0] == 'rstr':
                val = randomword()
            else:
                raise Exception('Unknown random var type: %s' % is_rvar[0])
        try:
            data[key] = int(val)
        except ValueError:
            data[key] = val

    # Add debug option to enable url print
    # print '%s\t%s' % (url, data)
    return (url, data)


def process_response(response):
    # check for errors
    if not re.match('2\d\d', str(response.status_code)):
        # check for conflicts
        if re.match('409', str(response.status_code)):
            try:
                registry['conflicts'] += 1
            except KeyError:
                registry['conflicts'] = 1
        else:
            # inrement error counter
            try:
                registry['errors'] += 1
            except KeyError:
                registry['errors'] = 1

    # check for cache headers
    if 'x-cache' in response.headers:
        if response.headers['x-cache'] == 'HIT':
            try:
                registry['hit'] += 1
            except KeyError:
                registry['hit'] = 1
        else:
            try:
                registry['miss'] += 1
            except KeyError:
                registry['miss'] = 1
    else:
        try:
            registry['uncached'] += 1
        except KeyError:
            registry['uncached'] = 1


def display_results(start_time):
    # result's metrics
    hit = registry.get('hit', 0)
    miss = registry.get('miss', 0)
    uncached = registry.get('uncached', 0)
    total_req = hit + miss + uncached

    print '\n'
    print 'Requests\t | %s' % total_req
    print '-------------------------'
    print 'Conflicts\t | %s' % registry.get('conflicts', 0)
    print 'Errors\t\t | %s' % registry.get('errors', 0)
    print '-------------------------'
    print 'Hit | Miss\t | %s | %s' % (hit, miss)
    print 'Uncached\t | %s' % uncached
    print '-------------------------'
    print 'Time %16.2f secs' % total_time(start_time)
    print '\n'


def total_time(start):
    return (time.time() - start)


def randomint():
    return random.randint(1, 99999)


def randomword():
    return ''.join(random.choice(string.lowercase) for i in range(8))


def main(filename):
    f = open(filename)
    for line in f.readlines():
        if line in ['\n'] or line.startswith('#'):
            continue
        fields = line.split(' ')
        token = fields[0]
        if token in tags:
            scenario_steps.append(fields)
        else:
            val = fields[1].strip()
            try:
                registry[token] = int(val)
            except ValueError:
                registry[token] = val

    start_time = time.time()
    for i in range(0, registry['repeat']):
        for step in scenario_steps:
            do_request(step)

    display_results(start_time)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "argument missing: cache test scenario file name."
    else:
        main(sys.argv[1])

#Add command line option to view URL constructed for requests
