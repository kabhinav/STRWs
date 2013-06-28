STRWs
=====

STRWs: Scenario Tester for ReSTful WebSevices

In the requests declaration of a scenario, {var} represents a variable with random value.
The types of a variable are:
 1. {rint} represents a random integer variable.
 2. {rstr} represents a random string variable.
 3. {print} represents persistent random integer whose value remain same across multiple requests.
All variables are  substituted with the values, either computed randomly or retrieved from
persisted source before making a HTTP request.

Installation
____________
```bash
$ git clone https://github.com/kabhinav/STRWs
$ cd STRWs
$ pip install requests
```

Usage
_____
```bash
$ cd STRWs/strws
$ python strws.py scenario.txt
```

Example: scenario.txt
_____________________
```
# Scenario 1: brief description of this test scenario: aim, resources involved etc.

# Configuration variables
server http://127.0.0.1:6542
resource_id 1234
subresource_id 1

# Number of times following test scenario will be repeated
repeat 10

# Requests
GET 1 /resource/{resource_id}/subresource/{subresource_id}
POST 1 /resource/{resource_id}/subresource/{subresource_id}/transactions name=test id={rint}
GET 1 /resource/{resource_id}/subresource/{subresource_id}/summary
PUT 1 /resource/{resource_id}/subresource/1 email={rstr} token={rstr} expires=10.0
GET 3 /resource/{resource_id}/subresource/{subresource_id}/summary
```

Output
______
```bash
Requests         | 100
-------------------------
Conflicts        | 18
Errors           | 0
-------------------------
Hit | Miss       | 0 | 0
Uncached         | 100
-------------------------
Time             1.45 secs
```