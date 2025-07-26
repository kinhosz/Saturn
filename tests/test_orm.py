from orm import Model, Fields

def test_chainlinkage(db_connection):
    sql = """
CREATE TABLE table_a (
    id                  SERIAL      PRIMARY KEY,
    name                VARCHAR(20) NOT NULL
);

CREATE TABLE table_b (
    id                  SERIAL      PRIMARY KEY,
    a_id                INTEGER     REFERENCES table_a(id)
);

CREATE TABLE table_c (
    id                  SERIAL      PRIMARY KEY,
    b_id                INTEGER     REFERENCES table_b(id)
);"""

    Model.manual(sql, False)

    class A(Model):
        _table = 'table_a'

        id = Fields.id()
        name = Fields.varchar()

    class B(Model):
        _table = 'table_b'

        id = Fields.id()
        a_id = Fields.reference('table_a')

    class C(Model):
        _table = 'table_c'

        id = Fields.id()
        b_id = Fields.reference('table_b')

    a1 = A()
    a1.name = "a1"
    a1.save()

    a2 = A()
    a2.name = "a2"
    a2.save()

    b1 = B()
    b1.a_id = a1.id
    b1.save()

    b2 = B()
    b2.a_id = a2.id
    b2.save()

    c = C()
    c.b_id = b1.id
    c.save()

    '''
               | -------> b1 ----------> a1
        c -----|
               | ---x---> b2 ----------> a2
    '''
    assert c.b_id.a_id.name == "a1"

    # b2.a_id is saved on the database
    c.b_id = b2.id
    '''
               | ---x---> b1 ----------> a1
        c -----|
               | -------> b2 ----------> a2
    '''
    assert c.b_id.a_id.name == "a2"

    # b2.a_id is not saved on memo
    b2.a_id = a1.id
    '''
               | ---x---> b1 ----------> a1
        c -----|
               | -------> b2 ----------> a2
    '''
    assert c.b_id.a_id.name == "a2"

    # Now, the a_id reference has been saved
    '''
               | ---x---> b1 ----------> a1
        c -----|                  |
               | -------> b2 -----|      a2
    '''
    b2.save()
    assert c.b_id.a_id.name == "a1"
