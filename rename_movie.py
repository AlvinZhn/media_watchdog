#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author ：Alvin
@Date   ：9/7/2019
@Desc   ：
"""
from helper import *
from model.Movies import Movies
from utils import my_logger as logger, wechat_logger


def creat_movie_symlink(file_path, name_from_db, extn, debug=False):
	# create path and symbolic link
	filename = os.path.split(file_path)[1]
	new_folder_path = config.symbolic_link_folder_path + "/Movies/" + name_from_db
	symbolic_path = new_folder_path + '/' + name_from_db + extn

	if not debug:
		make_dir(config.symbolic_link_folder_path)
		make_dir(config.symbolic_link_folder_path + "/Movies")
		make_dir(new_folder_path)

		if os.path.islink(symbolic_path):
			msg_code = 'code5'
			msg = "Symbolic Link Already Exist.\n"
			logger(msg + 'Filename: [{}], Symbolic Link: [{}].'.format(filename, symbolic_path))
			info = dict(
				status='Error',
				msg_code=msg_code,
				filename=filename,
				name_from_db=name_from_db,
			)
			return info
		else:
			os.symlink(file_path, symbolic_path)
			# add info to db
			m = Movies.new(dict(
				file_path=file_path,
				symbolic_path=symbolic_path
			))
			m.save()
			msg_code = 'code6'
			msg = 'Symbolic Link Build Successfully!\n'
			logger(msg + 'Filename: [{}], Symbolic Link: [{}].'.format(filename, symbolic_path))
			info = dict(
				status='Success',
				msg_code=msg_code,
				filename=filename,
				name_from_db=name_from_db,
			)
			return info
	else:
		if os.path.islink(symbolic_path):
			msg_code = 'code5'
			msg = "Debug: Symbolic Link Already Exist, You've download a duplicate file"
			print(msg)
			info = dict(
				status='Error',
				msg_code=msg_code,
				filename=filename,
				name_from_db=name_from_db,
			)
			return info
		else:
			m = Movies.new(dict(
				file_path=file_path,
				symbolic_path=symbolic_path
			))
			m.save()
			msg_code = 'code6'
			msg = 'Debug: Symbolic Link Build Successfully!'
			logger('{} File: [{}].'.format(msg, filename))
			info = dict(
				status='Success',
				msg_code=msg_code,
				filename=filename,
				name_from_db=name_from_db,
			)
			return info



def handle_movie_all(file_path_list, debug=False):
	"""
	:param file_info:
	:return:
	"""
	allowed_extn = config.allowed_extn
	allowed_extn.append('.nfo')
	result_list = []
	for file_path in file_path_list:
		# check if with a valid extension
		filename = os.path.split(file_path)[1]
		extn = os.path.splitext(filename)[1]
		media_type = 'Movie'

		if Movies.path_in_db(file_path):
			msg_code = 'code1'
			msg = 'File path exist in db.\n'
			logger('Skip file: [{}].'.format(filename))
			info = dict(
				status='Warning',
				msg_code=msg_code,
				filename=filename,
			)
			result_list.append(info)
			continue

		if extn in allowed_extn:
			# find appropriate name from imdb
			formatted_name = format_filename(filename, media_type)
			logger('formatted name: {}'.format(formatted_name))

			year_str = '(' + formatted_name[len(formatted_name) - 4: len(formatted_name)] + ')'
			logger('year_str name: {}'.format(year_str))

			formatted_name = formatted_name[0:len(formatted_name) - 4]
			final_name = formatted_name + year_str
			logger('Derived name: {}'.format(final_name))

			movies_name = search_from_imdb(final_name, media_type)

			if movies_name is None:
				msg_code = 'code3'
				msg = 'Error occurred while searching\n'
				logger(msg + 'Filename: [{}], Search Keyword: [{}].'.format(filename, final_name))
				info = dict(
					status='Error',
					msg_code=msg_code,
					filename=filename,
					final_name=final_name
				)
				result_list.append(info)
				continue
			elif len(movies_name) == 0:
				msg_code = 'code4'
				msg = 'No data found from imdb.\n'
				logger(msg + 'Filename: [{}], Search Keyword: [{}].'.format(filename, final_name))
				info = dict(
					status='Error',
					msg_code=msg_code,
					filename=filename,
					final_name=final_name
				)
				result_list.append(info)
				continue

			name_from_db = find_most_apt(final_name, movies_name)
			name_from_db = remove_illegal(name_from_db)
			logger("Most Apt: {}".format(name_from_db))

			creat_movie_symlink(file_path, name_from_db, extn, debug=debug)

		else:
			msg_code = 'code3'
			msg = 'File extn not allowed, are you missing something?'
			logger(msg + 'Filename: [{}].'.format(filename))
			info = dict(
				status='Error',
				msg_code=msg_code,
				filename=filename,
			)
			result_list.append(info)
			continue

	return result_list


def rename_movie(file_path_list=None, file_path=None, debug=False):
	"""
	:param file_path_list:
	:param file_path:
	:param debug:
	:return: a list of dicts
	"""
	if file_path is not None:
		result_list = handle_movie_all([file_path], debug=debug)
	elif file_path_list is not None:
		result_list = handle_movie_all(file_path_list, debug=debug)
	else:
		wechat_logger(title='参数错误', desp='method: `rename_movie`\n`file_path_list and file_path` are both `None`\n')
		raise KeyError
	return result_list
