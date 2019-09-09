#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author ：Alvin
@Date   ：8/27/2019
@Desc   ：
"""

from model import Model

class Series(Model):
	def __init__(self, path_info):
		self.file_path = path_info.get('file_path')
		self.symbolic_path = path_info.get('symbolic_path')