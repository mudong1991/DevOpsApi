# -*- coding: UTF-8 -*-
"""
 File Instruction
"""
__author__ = 'MD'
import re
from django.conf import settings
from django.core.validators import ValidationError
from django.utils.deconstruct import deconstructible

# 匹配特殊字符的正则表达式
NAME_REGEX_EXPRESSION = u'[^a-zA-Z0-9\u4E00-\u9FA5]'
DEFAULT_NAME_ERROR = "不能包含特殊字符"


@deconstructible
class AlwaysEqual(object):
    def __init__(self, func):
        self.func = func

    def __eq__(self, other):
        return True

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)


def validate_wrap(func):
    """
    为了让migrations不无限增加
    :param func:
    :return: AlwaysEqual
    """
    def _wrap(*args, **kwargs):
        return AlwaysEqual(func(*args, **kwargs))

    return _wrap


def _make_unicode(value):
    """
    :param value:
    :return: unicode value
    """
    try:
        ret = unicode(value)
    except:
        ret = unicode(value.decode("utf-8"))
    return ret


@validate_wrap
def validator_names_length(label_name):
    """
    名称类 字符串 长度验证器
    :param label_name:
    :return: function
    """
    return generator_value_length_validate(label_name, 1, 64)


@validate_wrap
def generator_value_length_validate(label_name, min_length=None, max_length=None):
    """
    检验值长度 验证函数生成
    :param label_name: 失败后输出的标签名称
    :param min_length: 最小长度
    :param max_length: 最大长度
    :return: function
    """

    def value_length_validator(value):
        try:
            label_length = len(_make_unicode(value))
        except:
            # 无法使用len获取value的长度
            pass

        # 最大值和最小值至少有一个有值
        if min_length is not None or max_length is not None:
            if min_length and max_length:
                if min_length > max_length:
                    if settings.DEBUG:
                        return ValidationError(message=u"最小长度不能大于最大长度！")
                else:
                    if label_length < min_length or label_length > max_length:
                        return ValidationError(message=u"{0}:长度应在{1}和{2}之间".format(label_name, min_length, max_length))
            if min_length and label_length < min_length:
                return ValidationError(message=u"{0}：长度不应小于{1}".format(label_name, min_length))
            if max_length and label_length > max_length:
                return ValidationError(message=u"{0}：长度不应大于{1}".format(label_name, max_length))
        # 最大值和最小值都为空
        else:
            pass

    return value_length_validator


def regex_validator(expression, value):
    """
    正则表达式匹配

    :param expression: 正则表达式
    :param value: 要匹配的字符串
    :return bool: 返回布尔值
    """
    p = re.compile(expression)
    if p.search(value):
        return True
    else:
        return False


@validate_wrap
def generator_value_length_validate(label_name, min_length=None, max_length=None):
    """
    检验值长度 验证函数生成

    :param label_name: 失败后输出的标签名称
    :param min_length: 最小长度
    :param max_length: 最大长度
    :return: function
    """

    def value_length_validator(value):
        try:
            len_value = len(_make_unicode(value))
        except:
            # 无法使用len获取value的长度
            pass

        if max_length < min_length:
            if settings.DEBUG:
                raise ValueError("验证器的最大长度小于最小值")

        if min_length is None or max_length is None:
            # 只验证某一个 or Neither
            if min_length >= 0:
                if len_value < min_length:
                    raise ValidationError(message='{0}：长度应该不小于{1}'.format(label_name, min_length))
            if max_length >= 0:
                if len_value > max_length:
                    raise ValidationError(message='{0}：长度应该不大于{1}'.format(label_name, max_length))
        else:
            if len_value < min_length or len_value > max_length:
                raise ValidationError(
                    message='{0}：长度应该在{1}和{2}之间'.format(label_name, min_length, max_length))

    return value_length_validator

@deconstructible
class NameValidator(object):
    """
    名称验证类

    :param label_name: 验证字段的中文释义 string
    :param min_length: 最小长度 integer
    :param max_length: 最大长度 integer
    :param expression: 正则表达式 string
    :param error_message: 正则表达式验证失败返回的错误消息 string
    :return:
    """

    def __init__(self, label_name, min_length=0, max_length=30, expression=NAME_REGEX_EXPRESSION,
                 error_message=DEFAULT_NAME_ERROR):

        if min_length > max_length:
            raise Exception("无效的限制范围")
        else:
            self.label_name = label_name
            self.min_length = min_length
            self.max_length = max_length
            self.expression = expression
            self.error_message = error_message

    def __call__(self, value):
        """
        :param value: 需要验证的值
        :return: None
        """
        if value is not None:
            try:
                len_of_value = len(_make_unicode(value))
            except Exception as e:
                print(e)
                raise ValidationError(message="{name}:非法字符串".format(name=self.label_name))

            if len_of_value > self.max_length or len_of_value < self.min_length:
                raise ValidationError(message="{name}:长度应该在{mi}-{ma}之间，您输入的长度为{length}".format(
                    name=self.label_name, mi=self.min_length, ma=self.max_length, length=len_of_value
                ))
            else:
                if regex_validator(self.expression, value):
                    raise ValidationError(
                        message="{name}:{value}".format(name=self.label_name, value=self.error_message))
        else:
            raise ValidationError(message="{name}:长度应该在{mi}-{ma}之间，您输入的长度为0".format(
                name=self.label_name, mi=self.min_length, ma=self.max_length
            ))

    def __eq__(self, other):
        return True


# django规定序列化规则必须绑定到body里面，否则会报错
def value_length_validator(value):
    pass
