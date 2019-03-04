import pymysql
from DBUtils.PooledDB import PooledDB
from ..config.mysql_config import set_mysql_config


# from ..config.mysql_config import set_mysql_config
#  pip install pymysql  python3连接mysql数据库的
#  pip install DBUtils   数据库连接池

# 创建数据库连接池
def create_pool():
    db_config = set_mysql_config("dev")
    return PooledDB(
        pymysql,
        5,
        host=db_config["host"],
        user=db_config["user"],
        passwd=db_config["passwd"],
        db=db_config["db"],
        port=db_config["port"],
        charset=db_config["charset"]
    ).connection()


# 执行sql语句的方法，两个参数，第一个是sql语句，第二个是sql语句中的参数
def execute(sql, args):
    try:
        connection = create_pool()
        cursor = connection.cursor()
        cursor.execute(sql.replace('?', '%s'), args)
        connection.commit()
        print("sql语句执行完毕SQL:" + sql + "参数是" + str(args))
        affected = cursor.rowcount
    finally:
        cursor.close()
        connection.close()

    return affected


class Field(object):
    def __init__(self, column_name, column_type):
        self.column_name = column_name
        self.column_type = column_type


class StringField(Field):
    def __init__(self, column_name):
        super(StringField, self).__init__(column_name, "varchar(200)")


class IntegerField(Field):
    def __init__(self, column_name):
        super(IntegerField, self).__init__(column_name, "bigint")


# 定义元类，控制model对象的创建
class ModelMetaClass(type):
    """
    关于type的说明
    name : 代表的是类名    贫僧唐三藏   代表了我是谁
    bases : 父类，元组   从东土大唐而来    代表我从哪里来
    dict: 类的属性和方法的值组成的键值对   前方西天取经   代表我要做什么
    唐三藏的故事： 施主你好，贫僧法号三藏，从东土大唐而来，前方西天取经
    """

    def __new__(cls, table_name, bases, attrs):
        if table_name == "Model":
            return super(ModelMetaClass, cls).__new__(cls, table_name, bases, attrs)
        # 用来保存类属性和列的映射关系
        mappings = dict()

        for k, v in attrs.items():

            # 保存类属性和列的映射关系到mappings字典中
            if isinstance(v, Field):
                mappings[k] = v  # 属性名称： 字段名，列名

        # 将类属性移除，使定义的类字段不受污染，只有实例中可以访问这些key
        # 用User.key 这种不能访问
        for k in mappings.keys():
            attrs.pop(k)

        attrs['__table__'] = table_name.lower()
        attrs['__mappings__'] = mappings
        return super(ModelMetaClass, cls).__new__(cls, table_name, bases, attrs)


# 编写一个model基类，这个类用于被具体的model对象继承。
# 实现具体的增删改查方法
# 好处是这样以后的每一个model就都有了这些方法
class Model(dict, metaclass=ModelMetaClass):
    def __init__(self, **kwargs):
        super(Model, self).__init__(**kwargs)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("你这个'Model'里边没有'%s'这个属性,好好看一看" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def insert(self):
        fields = []
        params = []
        args = []
        for k, v in self.__mappings__.items():
            fields.append(v.column_name)
            params.append('?')
            args.append(getattr(self, k))

        sql = 'insert into %s (%s) values (%s)' % (self.__table__, ','.join(fields), ','.join(params))
        res = execute(sql, args)
        print("sql语句执行成功,影响行数是" + str(res))

    def select(self):
        pass

    def update(self):
        pass
