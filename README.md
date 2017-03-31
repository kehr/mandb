Mandb
======

Mandb 是从 `Torndb` fork 过来的。

`Torndb` 只支持 MySQL 且不支持数据库连接池，但对数据库操作封装很好，于是便在其基础上拓展了`Mandb`，并支持 SQLite3。

Installation
------------

``pip install mandb``

Usage
-------------

```python

from mandb import SqliteDatabase
from mandb import MySQLDatabase

## for sqlite
db = SqliteDatabase('test.db')
## for MySQL
db = MySQLDatabase(
    host='localhost',
    port=3306,
    user='root',
    passwd='passwd',
    db='test_db',
    charset='utf8'
    )

## 1. Query data
print db.query('SELECT * FROM `sometable`')
# or
for row in db.query('SELECT * FROM `sometable`'):
    print row
## 2. Update data
print db.insert('INSERT INTO `sometable` VALUES(1,2,3,4)')
print db.update('UPDATE `sometable` SET var1=10 WHERE id=1')
print db.delete('DELETE * FROM `sometable`')

```
如果你在用 DBUtils 提供的数据库连接池:

```python
import MySQLdb
from mandb import Database
from DBUtils.PooledDB import PooledDB

pdb = PooledDB(MySQLdb,
            mincached=5,
            host='localhost',
            port=3306,
            user='root',
            passwd='passwd',
            db='test_db',
            charset='utf8')
db = Database(pdb.connection())
...
```

