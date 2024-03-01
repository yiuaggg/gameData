# coding=utf-8
import redis
from config import *


class Redis(object):
    """
    redis 调用类
    """
    def __init__(self, db_index):
        self.redis_obj = redis.StrictRedis(host=REDIS_HOST, password=REDIS_PASSWORD, port=REDIS_PORT,
                                           decode_responses=True, charset='utf8', encoding='utf8', db=db_index)

    def get_value(self, key):
        """
        获取单个键的值
        """
        value = self.redis_obj.get(key)
        return value
    
    def insert_data(self, key, value, ex=None):
        """
        插入数据
        """
        self.redis_obj.set(key, value, ex=ex)
    
    def get_all_value(self):
        """
        获取所有数据
        """
        values_list = []
        keys = self.redis_obj.keys()
        for key in keys:
            value = self.get_value(key)
            values_list.append(value)
        return values_list
    
    def have_exists(self, key):
        """
        检查键是否存在
        """
        is_exist = self.redis_obj.exists(key)
        return is_exist

    def del_value(self, key):
        """
        删除键值
        """
        self.redis_obj.delete(key)

    def clear_db(self):
        """
        清除数据库
        """
        self.redis_obj.flushdb()

    def insert_list(self, key, values):
        """
        以集合方式存储
        """
        if isinstance(values, list):
            pipe = self.redis_obj.pipeline(transaction=True)
            for value in values:
                pipe.sadd(key, value)
            result = pipe.execute()
            add_num = 0
            for item in result:
                add_num += item
            return int(add_num)
        else:
            return int(self.redis_obj.sadd(key, values))
    
    def get_list(self, key):
        """
        获取集合
        """
        list_data = self.redis_obj.smembers(key)
        return list(list_data)

    def set_diff(self, set1, set2):
        """
        计算两个集合的差集,set1中有而set2中没有
        """
        diff_data = self.redis_obj.sdiff(set1, set2)
        return list(diff_data)

    def del_set_value(self, set, value):
        """
        删除set中的某个值
        """
        self.redis_obj.srem(set, value)

    def get_key_ex(self, key):
        """
        获取 key 的过期时间
        :param key:
        :return:
        """
        return int(self.redis_obj.ttl(key))

    def get_values(self):
        """
        获取所有值
        :return:
        """
        values = []
        for key in self.redis_obj.keys():
            values.append(self.redis_obj.get(key))
        return values


if __name__ == '__main__':
    print(Redis(9).get_key_ex('f18d1065d30e059e14bf572481423ffb'))
