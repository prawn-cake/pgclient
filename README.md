![pgclientIcon](https://www.dropbox.com/s/4l91lo7kt5xor4w/elephant_64.png?dl=1) pgclient
========================================================================================
[![Build Status](https://travis-ci.org/prawn-cake/pgclient.svg?branch=master)](https://travis-ci.org/prawn-cake/pgclient)
[![Coverage Status](https://coveralls.io/repos/prawn-cake/pgclient/badge.svg?branch=master&service=github)](https://coveralls.io/github/prawn-cake/pgclient?branch=master)
![PythonVersions](https://www.dropbox.com/s/ck0nc28ttga2pw9/python-2.7_3.4-blue.svg?dl=1)

pgclient - yet another pool-based python2/3 compatible psycopg2 wrapper. 

The client is fully based on thread-safe reliable connections pool and safe transactions executing

*Tested on python2.7+, python3.4+*


Quick start
===========

### System dependencies: ###

* python-dev
* libpq-dev
 

### Install the package ###
    
    pip install pgclient


### Initialize the client ###

    from pgclient import PostgresClient
    
    
    pg_client = PostgresClient(dsn='user=admin password=admin dbname=test host=localhost port=5432')
    # OR
    pg_client = PostgresClient(username='test', password='test', ...)
    
    with self.pg_client.get_cursor() as cursor:
        cursor.execute('SELECT * FROM MyTable')
        
    result_set = cursor.fetchall()

Database requests
--------------------
    
**Assume that we use the following sql schema:**
    
    CREATE TABLE users (
        id SERIAL, 
        username VARCHAR NOT NULL 
    )

    
**Cursor context manager**

    with self.pg_client.get_cursor() as cursor:
        cursor.execute('SELECT * FROM users')

    users = cursor.fetchall()
    username = users[0]['username']     
    
**NOTE:** Default *cursor_factory* is `psycopg2.extras.RealDictCursor`
    
To override default factory, there are two ways:

* Override default one for client instance

        pg_client = PostgresClient(..., cursor_factory=psycopg2.extras.NamedTupleCursor)
    
* Override for context

        with pg_client.get_cursor(cursor_factory=MyCursor) as cursor:
            cursor.execute('SELECT * FROM users')
        

Safe transactions
-----------------

All requests inside `with` context will be executed and automatically committed within one transaction 
(or rolled back in case if database errors)
    
    with self.pg_client.get_cursor() as transaction:
        transaction.execute('INSERT INTO users VALUES name="Mark"')
        transaction.execute('INSERT INTO users VALUES name="Paolo"')
        transaction.execute('SELECT * FROM users')

    users = transaction.fetchall()
    
    
Auto-reconnect connection pool
------------------------------
Starting a new transaction, it guarantees that connection is alive

    with self.pg_client.get_cursor() as cursor:
        # connection is alive
        cursor.execute(...)
    
    # Or manually
    conn = self.pg_client.acquire_conn()
    conn.execute(...)
    ...
    self.pg_client.release_conn(conn)
    
    
Extended errors
---------------

Instead of basic `psycopg2.Error` based errors, [Extended exception classes](http://www.postgresql.org/docs/current/static/errcodes-appendix.html#ERRCODES-TABLE) have been added.
So now you will get more meaningful error information in case of any errors during 
the postgres communication and use error handling in more flexible way.

Example:
    
    from pgclient import exceptions as pg_exc
    
    try:
        with self.pg_client.get_cursor() as transaction:
            transaction.execute(...)
    except pg_exc.IntegrityConstraintViolation as err:
        logger.error(err.message, err.diag, err.pgcode)
    except pg_exc.DataException as err:
        ...

To catch all errors:
    
    try:
        with self.pg_client.get_cursor() as transaction:
            transaction.execute(...)
    except pg_exc.PgClientError as err:
        logger.error(err)
        ... 

System test
===========
To run integration test you need to install the following:
 
* [Docker](https://www.docker.com/) 
* [Docker compose](https://docs.docker.com/compose/)


**Run system test:**

* Run postgresql container: `docker-compose up -d postgresql`
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
