# -*- coding:utf-8 -*-
# file: serializers
# author: Mundy
# date: 2017/11/8 0008
from rest_framework import serializers
from urlparse import urlparse
from django.conf import settings
from firstapp import models
from firstapp.util_aes import aes_api_data_encrypt, aes_html_data_decrypt
from firstapp import cust_exceptions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'
