#!/usr/bin/env python
#
# Copyright 2016 Kehr<kehr.china@gmail.com>
# Reference: torndb, DBUtils

"""`Mandb` is a lightweight wrapper around `MySQLdb` and `sqlite3`.

    This lib is inspired by `torndb` and `DBUtils`. It supports DBUtils to manage your exists
    connection. If you has any good ideas, please contact me <kehr.china@gmail.com>

"""

import sqlite3
import MySQLdb
import threading

version = '0.1.3'
version_info = (0, 1, 3, 0)


class MandbEception(Exception):
    """Base exception for mandb"""
    pass


class Row(dict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


class Database(object):
    """This class provide a series of base database operations. It can manage your
    connection, if you already has one.

    Example::

        import MySQLdb
        from mandb import Database
        from DBUtils.PooledDB import PooledDB

        pdb = PooledDB(MySQLdb, host='localhost', port=3306, db='test_db',
                    user='root', passwd='passwd', mincached=5, charset='utf8')
        db = Database(pdb.connection())
        db.query('SELECT ...')
        db.insert('INSERT INTO ...')
        db.update('UPDATE ...')
        db.delete('DELETE ...')
        ...

    Otherwise, please use `MySQLDatabase` or `SqliteDatabase` to create a new connection.
    """
    def __init__(self, connection=None, **kwargs):
        """
        Args:
            :connection: Specify an exists database connection.
            :kwargs: Connection parameters.
        """
        self.connection = connection
        self.kwargs = kwargs
        self._closed = True
        self._conn_lock = threading.Lock()
        self.connect()

    def __del__(self):
        self.close()

    def connect(self):
        """Get this database connection"""
        with self._conn_lock:
            self._closed = False
            if self.connection is None:
                self.connection = self._connect()
            # Ensure auto commit
            if hasattr(self.connection, 'autocommit'):
                self.connection.autocommit(True)
            # Autocommit setting for DBUtils
            elif hasattr(self.connection, '_con') and hasattr(self.connection._con, '_con'):
                self.connection._con._con.autocommit(True)


    def close(self):
        """Closes this database connection"""
        with self._conn_lock:
            if self.connection is not None:
                self.connection.close()
                self.connection = None
                self._closed = True

    def is_closed(self):
        """Return if connnection is closed"""
        return self._closed

    def iter(self, sql, *args, **kwargs):
        """Returns an iterator for the given query and parameters."""
        cursor = self._cursor()
        try:
            self._execute(cursor, sql, args, kwargs)
            names = [d[0] for d in cursor.description]
            for row in cursor:
                yield Row(zip(names, row))
        finally:
            cursor.close()

    def query(self, sql, *args, **kwargs):
        """Returns a row list for the given query and parameters."""
        cursor = self._cursor()
        try:
            self._execute(cursor, sql, args, kwargs)
            names = [d[0] for d in cursor.description]
            return [Row(zip(names, row)) for row in cursor]
        finally:
            cursor.close()

    def get(self, sql, *args, **kwargs):
        """Returns the (singular) row returned by the given query.

        If the query has no results, returns None.  If it has
        more than one result, raises an exception.
        """
        rows = self.query(sql, *args, **kwargs)
        if not rows:
            return None
        elif len(rows) > 1:
            raise MandbEception('Multiple rows returned for Database.get() query')
        else:
            return rows[0]

    def execute(self, sql, *args, **kwargs):
        """Executes the given sql, returning the lastrowid."""
        return self.execute_lastrowid(sql, *args, **kwargs)

    def rollback(self):
        """Rolls backs the current transaction"""
        self.connection.rollback()

    def execute_lastrowid(self, sql, *args, **kwargs):
        """Executes the given sql, returning the lastrowid."""
        cursor = self._cursor()
        try:
            self._execute(cursor, sql, args, kwargs)
            return cursor.lastrowid
        finally:
            cursor.close()

    def execute_rowcount(self, sql, *args, **kwargs):
        """Executes the given query, returning the rowcount."""
        cursor = self._cursor()
        try:
            self._execute(cursor, sql, args, kwargs)
            return cursor.rowcount
        finally:
            cursor.close()

    def executemany(self, sql, args):
        """Executes the given query against all the given param sequences."""
        return self.executemany_lastrowid(sql, args)

    def executemany_lastrowid(self, sql, args):
        """Executes the given query against all the given param sequences."""
        cursor = self._cursor()
        try:
            cursor.executemany(sql, args)
            return cursor.lastrowid
        finally:
            cursor.close()

    def executemany_rowcount(self, sql, args):
        """Executes the given query against all the given param sequences."""
        cursor = self._cursor()
        try:
            cursor.executemany(sql, args)
            return cursor.rowcount
        finally:
            cursor.close()

    update = delete = execute_rowcount
    updatemany = executemany_rowcount

    insert = execute_lastrowid
    insertmany = executemany_lastrowid

    def _connect(self):
        """Connect to Database(eg. mysql, sqlite). Need rewrite"""
        raise NotImplementedError

    def _cursor(self):
        """Get the cursor of connection.

        Default use DB-API standard.
        """
        return self.connection.cursor()

    def _execute(self, cursor, sql, args, kwargs):
        """execute sql by cursor.

        Default use DB-API standard.
        """
        return cursor.execute(sql, kwargs or args or None)


class SqliteDatabase(Database):
    """Subclass of `Database`, wrapper for Sqlite3

    usage::

        from mandb import SqliteDatabase

        db = SqliteDatabase(db='test.db')
        db.query('SELECT ...')
        db.insert('INSERT INTO ...')
        db.update('UPDATE ...')
        db.delete('DELETE ...')
        ...
    """
    def __init__(self, db, *args, **kwargs):
        """
        Args:
            :db: The sqlite database file.
        """
        self.database = db
        super(SqliteDatabase, self).__init__(*args, **kwargs)

    def _connect(self):
        conn = sqlite3.connect(self.database, **self.kwargs)
        # This setting means `autocommit`
        conn.isolation_level = None
        return conn


class MySQLDatabase(Database):
    """Subclass of `Database`, wrapper for MySQL

    usage::

        from mandb import MySQLDatabase

        db = MySQLDatabase(host='localhost', port=3306,  db='test',
                           user='root', passwd='123456', charset='utf8')
        db.query('SELECT ...')
        db.insert('INSERT INTO ...')
        db.update('UPDATE ...')
        db.delete('DELETE ...')
        ...
    """
    def __init__(self, *args, **kwargs):
        super(MySQLDatabase, self).__init__(*args, **kwargs)

    def _connect(self):
        return MySQLdb.connect(**self.kwargs)
