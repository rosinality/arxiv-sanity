from peewee import *
from playhouse.pool import PooledSqliteDatabase

database = SqliteDatabase(
    'arxiv.db',
    pragmas={
        'journal_mode': 'wal',
        'cache_size': -1 * 64000,  # 64MB
        'foreign_keys': 1,
        'ignore_check_constraints': 0,
    },
)


class UnknownField(object):
    def __init__(self, *_, **__):
        pass


class BaseModel(Model):
    class Meta:
        database = database


class Papers(BaseModel):
    authors = TextField(null=True)
    category = TextField(null=True)
    id = TextField(null=True, primary_key=True)
    new = IntegerField(constraints=[SQL("DEFAULT 1")], null=True)
    published = IntegerField(index=True, null=True)
    state = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    summary = TextField(null=True)
    title = TextField(null=True)
    updated = IntegerField(index=True, null=True)
    version = IntegerField(null=True)

    class Meta:
        table_name = 'papers'


class Authors(BaseModel):
    author = TextField(null=True)
    paper = ForeignKeyField(column_name='paper', field='id', model=Papers, null=True)

    class Meta:
        table_name = 'authors'
