#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author ：Alvin
@Date   ：8/26/2019
@Desc   ：watchdog server
"""

import os
import time

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from Rename_All import rename_all

from utils import send_to_wechat, wechat_logger
from utils import my_logger as logger

from model.Series import Series
from model.Movies import Movies

import config


def init_db(db_folder_path):
	os.mkdir(db_folder_path)

	with open(os.path.join(db_folder_path, 'Movies.txt'), 'w', encoding='utf-8') as m:
		m.write(str('[]'))

	with open(os.path.join(db_folder_path, 'Series.txt'), 'w', encoding='utf-8') as s:
		s.write(str('[]'))


def init_server():
	media_folder_path = config.media_folder_path
	file_path_dict = dict(
		Movie=[],
		Series=[]
	)
	for root, dirs, files in os.walk(media_folder_path, topdown=True):
		dirs[:] = [d for d in dirs if d not in config.exclude_folder]
		media_type = 'Movie' if '/Movie' in root else 'Series'
		for filename in files:
			if ('.' + str(filename).split('.')[-1]) in config.allowed_extn:
				file_path_dict[media_type].append(os.path.join(root, filename))

	db_folder_path = str(os.getcwd()) + "/db"
	if not os.path.isdir(db_folder_path):
		logger('No DB found, starting to init database...')
		init_db(db_folder_path)
		# scan all files
		callback_info = rename_all(file_path_dict)
		status = 'init'
		send_to_wechat(callback_info, status)
	else:
		# check validity of all symbolic link
		logger('Check Broken Symbolic Link...')
		broken_file_path = []
		instance_list = []
		instance_list += Series.symlink_validation()
		instance_list += Movies.symlink_validation()
		for el in instance_list:
			file_path = getattr(el, 'file_path')
			logger('File [{}] not exist, remove relevant symbolic link, remove instance from db...'.format(file_path))
			broken_file_path.append(file_path)
		if len(broken_file_path) != 0:
			msg = "###Broken symbolic link detected\n" \
				  "__Notice:__ _Below files were deleted from database due to file missing._\n"
			for file_path in broken_file_path:
				msg += "* `{}`\n\n".format(file_path)
			wechat_logger(title='数据库变动通知', desp=msg)

		# check db modification
		logger('Check File Modification...')
		series_path_list = Series.check_modification(file_path_dict.get('Series'))
		movie_path_list = Movies.check_modification(file_path_dict.get('Movie'))
		file_path_dict = dict(
			Movie=movie_path_list,
			Series=series_path_list
		)
		# scan remain files
		callback_info = rename_all(file_path_dict)
		status = 'check'
		send_to_wechat(callback_info, status)


class MyHandler(PatternMatchingEventHandler):
	def __init__(self):
		super(MyHandler, self).__init__(patterns=config.watched_patterns, ignore_patterns=config.exclude_folder,
										ignore_directories=True)

	def on_moved(self, event):
		super(MyHandler, self).on_moved(event)
		logger('Moved file: from %s to %s', event.src_path, event.dest_path)
		# get file info from src_path
		file_path = event.dest_path
		if '/Movie/' in file_path:
			media_type = 'Movie'
		elif '/Series/' in file_path:
			media_type = 'Series'
		else:
			wechat_logger(title='类型错误', desp='method: `on_moved`\n`Movie and Series` are both not in `file_path`\n')
			raise TypeError
		file_path_dict = dict(
			Movie=[],
			Series=[]
		)
		if (os.path.splitext(file_path[0])[1]) in config.allowed_extn:
			file_path_dict[media_type].append(file_path)
			# rename new file
			callback_info = rename_all(file_path_dict)
			# wechat send info to inform file download & rename success
			status = 'moved'
			send_to_wechat(callback_info, status)


if __name__ == "__main__":
	init_server()
	logger('Starting to monitoring media path...')

	path = config.media_folder_path

	event_handler = MyHandler()
	observer = Observer()
	observer.schedule(event_handler, path, recursive=True)
	observer.start()
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		observer.stop()
	observer.join()
