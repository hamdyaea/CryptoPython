This is a blockchain in Python3.    
    

You can try it there :    https://astrometry.pythonanywhere.com
   
   
Developer : Hamdy Abou El Anein    
hamdy.aea@protonmail.com   



## Reviewed local demo

Install `requirements.txt` and run `python3 app.py`. Importing the app does not modify a database. Default storage is `instance/blockchain.db`, overridable with `CRYPTOPYTHON_DB`; historical databases are not migrated or changed. Writes are disabled by default. Trusted local experiments may explicitly use `create_app(database, allow_writes=True)`; public writes require authentication, CSRF protection and rate limiting first. POST replaces the unsafe GET mutation. Appends use an SQLite immediate transaction to prevent concurrent forks. The read API returns at most 1,000 oldest blocks. This is a hash-chain example, not real cryptocurrency consensus.

Run `python3 -m unittest -v`: temporary databases only, including concurrent writers. No deployment or data migration.
