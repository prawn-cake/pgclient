![pgclientIcon](https://www.dropbox.com/s/4l91lo7kt5xor4w/elephant_64.png?dl=1) pgclient
========================================================================================
[![Build Status](https://travis-ci.org/prawn-cake/pgclient.svg?branch=master)](https://travis-ci.org/prawn-cake/pgclient)
[![Coverage Status](https://coveralls.io/repos/prawn-cake/pgclient/badge.svg?branch=master&service=github)](https://coveralls.io/github/prawn-cake/pgclient?branch=master)
![PythonVersions](https://www.dropbox.com/s/ck0nc28ttga2pw9/python-2.7_3.4-blue.svg?dl=1)

pgclient - yet another pool-based python2/3 compatible psycopg2 wrapper. 

The client is fully based on thread-safe connections pool and safe transactions executing

*Tested on python2.7+, python3.4+*


Quick start
===========

### System dependencies: ###

* python-dev
* libpq-dev
 

### Install the package ###
    
    pip install pgclient


### Initialize the client ###

    from pgclient.client import PostgresClient
    
    
    pg_client = PostgresClient(dsn='user=admin password=admin dbname=test host=localhost port=5432')
    # OR
    pg_client = PostgresClient(username='test', password='test', ...)
    
    with self.pg_client.cursor as cursor:
        cursor.execute('SELECT * FROM MyTable')
        
    result_set = cursor.fetchall()

Database requests
--------------------
    
**SQL Schema:**
    
    CREATE TABLE users (
        id SERIAL, 
        username VARCHAR NOT NULL 
    )

    
**Basic cursor**

Result set index based access

    with self.pg_client.cursor as cursor:
        cursor.execute('SELECT * FROM users')

    users = cursor.fetchall()
    username = users[0][0]  # (OR users[0][1])     
    
    
**Dict cursor**
    
    with self.pg_client.dict_cursor as cursor:
        cursor.execute('SELECT * FROM users')

    users = cursor.fetchall()
    user = users[0]
    print(user['name'])
        
        
**Named-tuple cursor**

    with self.pg_client.nt_cursor as cursor:
        cursor.execute('SELECT * FROM users')

    users = cursor.fetchall()
    user = users[0]
    print(user.name)

    
Safe transactions
-----------------

All requests inside `with` context will be executed and automatically committed within one transaction 
(or rolled back in case if database errors)
    
    with self.pg_client.cursor as transaction:
        transaction.execute('INSERT INTO users VALUES name="Mark"')
        transaction.execute('INSERT INTO users VALUES name="Paolo"')
        transaction.execute('SELECT * FROM users')

    users = transaction.fetchall()
    

System test
===========
To run integration test you need to install the following:
 
* [Docker](https://www.docker.com/) 
* [Docker compose](https://docs.docker.com/compose/)


**Run system test:**

* Run postgresql container: `docker-compose up  -d postgresql`
* Run system tests: `make system_test`
* Stop postgresql container: `docker-compose stop postgresql`

To test with *postgresql:9.0* run `postgresql_90` container with docker compose.

Both versions are being tested with travis ci.



Bug tracker
===========

Warm welcome to suggestions and concerns

https://github.com/prawn-cake/pgclient/issues


License
=======

MIT - http://opensource.org/licenses/MIT
