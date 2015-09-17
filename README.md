pgclient
=============

pgclient - yet another pool-based psycopg2 wrapper. 

The client is fully based on thread-safe connections pool and safe transactions executing


Quick start
===========
    
    from pgclient.client import PostgresClient
    
    
    pg_client = PostgresClient(dsn='user=admin password=admin dbname=test host=localhost port=5432')
    # OR
    pg_client = PostgresClient(username='test', password='test', ...)
    
    with self.pg_client.cursor as cursor:
        cursor.execute('SELECT * FROM MyTable')
        
    result_set = cursor.fetchall()

Database raw request
--------------------
    
Assume that test data schema is the following:

* TABLE:    users
* SCHEMA:   name: VARCHAR, id: INTEGER
    
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
    result = cursor.fetchall()
    
    user = users[0]
    print(user.name)

    
Safe transactions
-----------------

All requests inside `with` context will be executed and automatically committed within one transaction
    
    with self.pg_client.cursor as transaction:
        transaction.execute('INSERT INTO users VALUES name="Mark"')
        transaction.execute('INSERT INTO users VALUES name="Paolo"')
        transaction.execute('SELECT * FROM users')

    users = transaction.fetchall()
    

Installation
============
System dependencies
-------------------

Install the following dependencies via `.deb` or `.rpm` packages

* python-dev
* libpq-dev

Install package
---------------

    pip install pgclient


System test
===========
To run integration test you need to install the following:
 
* [Docker](https://www.docker.com/) 
* [Docker compose](https://docs.docker.com/compose/)


**Run system tests:**

* Run postgresql container: `docker-compose up  -d postgresql`
* Run system tests: `make system_test`
* Stop postgresql container: `docker-compose stop postgresql`


Bug tracker
===========

Warm welcome to suggestions and concerns

https://github.com/prawn-cake/pgclient/issues


License
=======

MIT - http://opensource.org/licenses/MIT
