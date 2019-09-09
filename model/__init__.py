#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author ：Alvin
@Date   ：8/27/2019
@Desc   ：
"""
import json
import os


def save(data, path):
	s = json.dumps(data, indent=2, ensure_ascii=False)
	with open(path, 'w+', encoding='utf-8') as f:
		# log('save', path, s, data)
		f.write(s)


def load(path):
	with open(path, 'r', encoding='utf-8') as f:
		s = f.read()
		# log('load', s)
		return json.loads(s)


class Model(object):
	@classmethod
	def db_path(cls):
		classname = cls.__name__
		path = 'db/{}.txt'.format(classname)
		return path

	@classmethod
	def new(cls, path_info):
		m = cls(path_info)
		return m

	@classmethod
	def all(cls):
		path = cls.db_path()
		models = load(path)
		ms = [cls.new(m) for m in models]
		return ms

	def save(self):
		models = self.all()
		models.append(self)

		l = [m.__dict__ for m in models]
		path = self.db_path()
		save(l, path)

	@classmethod
	def find_by(cls, **kwargs):
		# kwargs -> dict
		instances = cls.all()
		kw_numbers = len(kwargs)
		for el in instances:
			flag = False
			for i in range(kw_numbers):
				key = list(kwargs.keys())[i]
				if getattr(el, key) == kwargs[key]:
					flag = True
				else:
					flag = False
			if flag:
				return el
		return None

	@classmethod
	def delete(cls, file_path):
		ms = cls.all()
		for i, m in enumerate(ms):
			if getattr(m, 'file_path') == file_path:
				del ms[i]
				break
		l = [m.__dict__ for m in ms]
		path = cls.db_path()
		save(l, path)

	@classmethod
	def path_in_db(cls, file_path):
		r = cls.find_by(file_path=file_path)
		if r is None:
			return False
		else:
			return True

	@classmethod
	def symlink_validation(cls):
		delete_instances = []
		instances = cls.all()
		for el in instances:
			symbolic_path = getattr(el, 'symbolic_path')
			if os.path.exists(symbolic_path):
				continue
			else:
				# original file not exist, delete symbolic and remove data from db
				os.remove(symbolic_path)
				delete_instances.append(el)
		for instance in delete_instances:
			file_path = getattr(instance, 'file_path')
			cls.delete(file_path)
		return delete_instances

	@classmethod
	def check_modification(cls, path_list):
		delete_path = []
		for file_path in path_list:
			if cls.path_in_db(file_path):
				delete_path.append(file_path)
		for el in delete_path:
			path_list.remove(el)
		return path_list

	def __repr__(self):
		classname = self.__class__.__name__
		properties = ['{}: {}'.format(k, v) for k, v in self.__dict__.items()]
		s = '\n'.join(properties)
		return '< {}\n{} >\n'.format(classname, s)
