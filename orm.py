from enum import enum
from pluralize import pluralize
import pymysql

SQL_OPERATION = enum("SQL_SELECT", "SQL_UPDATE", "SQL_DELETE", "SQL_INSERT", "SQL_NULL")
BOOL_OPERATION = enum("OP_AND", "OP_OR", "OP_NULL")
GROUP_OPERATION = enum("LEFT_PARAN", "RIGHT_PARAN", "NULL_PARAM")

class Model(object):

    _has_many = []
    _has_one = []
    _related = []
    _related_field = []

    _operation = SQL_OPERATION.SQL_NULL


    class condition:
        operation = BOOL_OPERATION.OP_NULL
        next_cond = None
        group = False
        clause = ""
        def __init__(self, op, clause, group=GROUP_OPERATION.NULL_PARAM):
            self.operation = op
            self.clause = clause
            self.group = group
            self.clause = clause



    """
        users
        flavors
        user_flavors

        SELECT {FIELDS} FROM users
            INNER JOIN user_flavors ON user_flavors.user_id = users.id
            INNER JOIN flavors ON user_flavors.flavor_id = flavors.id

        SELECT {FIELDS} FROM self.tblname
            INNER JOIN self.tblname_model.tblname ON self.tblname_model.tblname.self.tblname_id = self.tblname.id
            INNER JOIN model.tblname ON self.tblname_model.tblname.model.tblname_id = model.tblname.id
    """
    _has_many_to_many = []


    def select(self, field, fas=None):
        return self

    def select_related(self, model, fields):
        return self

    def where(self, field, value=None):
        return self

    def or_where(self, field, value=None):
        return self

    def where_in(self, field, value):
        return self

    def or_where_in(self, field, value=None):
        return self

    def where_not_in(self, field, value=None):
        return self

    def or_where_not_in(self, field, value=None):
        return self

    def from_array(self, POST, keys):
        return self

    def like(self, field, value):
        return self

    def or_like(self, field, value):
        return self

    def not_like(self, field, value):
        return self

    def or_not_like(self, field, value):
        return self

    def ilike(self, field, value):
        return self

    def or_ilike(self, field, value):
        return self

    def not_ilike(self, field, value):
        return self

    def or_not_ilike(self, field, value):
        return self

    def limit(self, limit, start=0):
        return self

    def order_by(self):
        return self

    def select_max(self):
        return self

    def select_min(self):
        return self

    def select_avg(self):
        return self

    def select_sum(self):
        return self

    def distinct(self):
        return self

    def group_by(self):
        return self

    def having(self):
        return self

    def where_related(self, model, field):
        return self

    def save(self, force=False):
        return []

    def delete(self):
        return []

    def get(self):
        return []

    def query(self):
        """
            This method should be overwritten in child classes
        """
        raise NotImplementedError("Abstract method")

class SQLModel(Model):
    """
    @type self._where: Model.condition
    """
    _select = {}
    _where = None
    _resulting_query = ""
    _select_related = {}
    def select(self, field, fas=None):
        if fas:
            self._select[field] = fas
        else:
            self._select[field] = field
        return self

    def select_related(self, model, fields):
        if self._select_related.has_key(model):
            self._select_related[model].append(fields)
        else:
            self._select_related[model] = fields
        return self


    def _where_abs(self, field, value, op):
        if value:
            if type(value) == type(0):
                value = str(value)
            else:
                value = "'" + value + "'"
            if " " in field:
                cond = Model.condition(op, field + " " + value)
            else:
                cond = Model.condition(op, field + " = " + value)
        else:
            cond = Model.condition(op, field)
        if self._where:
            next = self._where
            while next:
                if not next.next_cond:
                    break
                next = next.next_cond
            next.next_cond = cond
        else:
            self._where = cond

    def _build_where(self):
        pointer = self._where
        if pointer:
            self._resulting_query += "WHERE "
        while pointer:
            if pointer.group is not None and pointer.group != GROUP_OPERATION.NULL_PARAM:
                if pointer.group == GROUP_OPERATION.LEFT_PARAN:
                    self._resulting_query += "( "
                elif pointer.group == GROUP_OPERATION.RIGHT_PARAN:
                    self._resulting_query += ") "
            else:
                self._resulting_query += pointer.clause + " "
                if pointer.next_cond:
                    if pointer.operation == BOOL_OPERATION.OP_AND:
                        self._resulting_query += "AND "
                    elif pointer.operation == BOOL_OPERATION.OP_OR:
                        self._resulting_query += "OR "

            pointer = pointer.next_cond


    def where(self, field, value=None):
        self._where_abs(field, value, BOOL_OPERATION.OP_AND)
        return self

    def where_in(self, field, value):
        self._where_abs(field + " IN (" + ",".join([str(v) for v in value]) + ")", None, BOOL_OPERATION.OP_AND)
        return self

    def or_where(self, field, value=None):
        self._where_abs(field, value, BOOL_OPERATION.OP_OR)
        return self

    def save(self, force=False):
        props = dir(self)
        tblname = pluralize(type(self).__name__)
        propdict = {}
        id = None
        if type(self).__name__ + "_id" in props:
            id = getattr(self, type(self).__name__ + "_id")

        for prop in self._select:
            attr = getattr(self, prop)
            if prop[0] == '_':
                continue
            propdict[prop] = getattr(self, prop)

        if id is not None:
            self._resulting_query = "UPDATE " + tblname + " SET "
            for k,v in propdict.iteritems():
                if type(v) == type(0):
                    self._resulting_query += k + " = " + v + ", "
                elif type(v) == type(""):
                    self._resulting_query += k + " = '" + v + "', "
            self._resulting_query = self._resulting_query.rstrip(', ') + " "
            self._build_where()
            if "WHERE" in self._resulting_query:
                self._resulting_query += "AND " + tblname + ".id = " + str(id) + " "
            else:
                self._resulting_query += "WHERE " + tblname + ".id = " + str(id) + " "
        else:
            self._resulting_query = "INSERT INTO " + tblname + " "
            self._resulting_query += "("
            for key in propdict.keys():
                self._resulting_query += key + ","
                self._resulting_query = self._resulting_query.rstrip(', ') + " "
            self._resulting_query += ") VALUES ("
            for val in propdict.values():
                if type(val) == type(0):
                    self._resulting_query += str(val) + ","
                else:
                    self._resulting_query += "'" + val + "',"
            self._resulting_query = self._resulting_query.rstrip(', ') + " "
            self._resulting_query += ")"
        return self._resulting_query


    def get(self):

        self._resulting_query = "SELECT "
        self._resulting_query += pluralize(type(self).__name__) + ".id AS " + type(self).__name__ + "_id, "
        for tbl in self._has_one:
            self._resulting_query += pluralize(type(tbl).__name__) + ".id AS " + type(tbl).__name__ + "_id, "
        if self._select:
            for k,v in self._select.iteritems():
                if v:
                    self._resulting_query += "%s AS %s, " % (k, v)
                else:
                    self._resulting_query += k + " "
            for i in self._select_related:
                self._resulting_query += i + ", "
            self._resulting_query = self._resulting_query.strip(", ") + " "
        else:
            self._resulting_query += "* "

        self._resulting_query += "FROM " + pluralize(type(self).__name__) + " "

        for tbl in self._has_many:
            tblname = pluralize(type(tbl).__name__)
            single = type(tbl).__name__
            self._resulting_query += "INNER JOIN %s ON %s = %s" % (tblname,
                                                                   tblname + "." + type(self).__name__ + "_id",
                                                                    type(self).__name__ + ".id") + " "
        for tbl in self._has_one:
            tblname = pluralize(type(tbl).__name__)
            single = type(tbl).__name__
            self._resulting_query += "INNER JOIN %s ON %s = %s" % (tblname,
                                                                   pluralize(type(self).__name__) + "." + single + "_id",
                                                                    tblname + ".id") + " "
        for tbl in self._has_many_to_many:
            jointbl = type(self).__name__ + "_" + pluralize(type(tbl).__name__)
            thissingle = type(self).__name__
            thisplural = pluralize(type(self).__name__)
            tblsingle = type(tbl).__name__
            tblplural = pluralize(type(tbl).__name__)
            self._resulting_query += "INNER JOIN %s ON %s = %s" % (jointbl,
                                                                 jointbl + "." + thissingle + "_id",
                                                                 thisplural + ".id") + " "
            self._resulting_query += "INNER JOIN %s ON %s = %s" % (tblplural,
                                                                   jointbl + "." + tblsingle + "_id",
                                                                   tblplural + ".id") + " "

        self._build_where()


        return self._resulting_query

class MySQLModel(SQLModel):
    def connect(self, host='127.0.0.1', port=3306, user='root', passwd='', db='mysql'):
        self.conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
        self.res = None


    def save(self, force=False):
        query = super(MySQLModel, self).save(force)
        c = self.conn.cursor()
        c.execute(query)
        self.conn.commit()
        c.close()

    def get(self):
        if not self.res:
            query = super(MySQLModel, self).get()
            self.c = self.conn.cursor(pymysql.cursors.DictCursor)
            self.c.execute(query)
        self.res = self.c.fetchone()

        if not self.res:
            #self._select = {}
            self._where = None
            self.c.close()
            return None

        if self._select == {}:
            if self.res:
                for k,v in self.res.iteritems():
                    setattr(self, k, v)
                res = self.c.fetchone()
        else:
            for i in self._select:
                if i in self.res:
                    setattr(self, i, self.res[i])
            setattr(self, type(self).__name__ + "_id", self.res[type(self).__name__ + "_id"])
            for k,v in self._select_related.iteritems():
                for i in self._has_one:
                    if type(i).__name__ == k:
                        i._select = {}
                        setattr(self, type(i).__name__, i)
                        for val in v:
                            i._select[val] = val
                            setattr(i, val, self.res[val])
                    setattr(i, type(i).__name__ + "_id", self.res[type(i).__name__ + "_id"])

        return True



class CSVModel(Model):
    pass
