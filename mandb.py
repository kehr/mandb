#!/usr/bin/env python
#
# Copyright 2016 Kehr<kehr.china@gmail.com>
# Reference: torndb, DBUtils

"""A lightweight wrapper around MySQLdb, sqlite3.

Mandb can be used with connection pool which like
DBUtils and has same api like torndb.
"""

import sqlite3
import MySQLdb
import logging
import threading

version = '0.1'
version_info = (0, 1, 0, 0)


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
    """Base database operation"""
    def __init__(self, connection=None, **kwargs):
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
        """Executes the given sql, returning the lastrowid from the sql."""
        return self.execute_lastrowid(sql, *args, **kwargs)

    def execute_lastrowid(self, sql, *args, **kwargs):
        """Executes the given sql, returning the lastrowid from the sql."""
        cursor = self._cursor()
        try:
            self._execute(cursor, sql, args, kwargs)
            return cursor.lastrowid
        finally:
            cursor.close()

    def execute_rowcount(self, sql, *args, **kwargs):
        """Executes the given query, returning the rowcount from the query."""
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
        raise NotImplementedError

    def _cursor(self):
        raise NotImplementedError

    def _execute(self, cursor, sql, args, kwargs):
        raise NotImplementedError


class SqliteDatabase(Database):
    """Database wrapper for Sqlite3"""
    def __init__(self, connection=None, *args, **kwargs):
        if 'database' not in kwargs:
            raise Exception('SqliteDatabase require `database` argument')
        self.database = kwargs.pop('database')
        super(SqliteDatabase, self).__init__(connection, *args, **kwargs)

    def _connect(self):
        conn = sqlite3.connect(self.database, **self.kwargs)
        # This setting means `autocommit`
        conn.isolation_level = None
        return conn

    def _cursor(self):
        return self.connection.cursor()

    def _execute(self, cursor, sql, args, kwargs):
        return cursor.execute(sql, kwargs or args)


class MySQLDatabase(Database):
    """Database wrapper for MySQL"""
    def __init__(self, connection=None, *args, **kwargs):
        super(MySQLDatabase, self).__init__(connection, *args, **kwargs)

    def _connect(self):
        conn = MySQLdb.connect(**self.kwargs)
        conn.autocommit(True)
        return conn

    def _cursor(self):
        return self.connection.cursor()

    def _execute(self, cursor, sql, args, kwargs):
        return cursor.execute(sql, kwargs or args)
