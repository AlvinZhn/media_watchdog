#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author ：Alvin
@Date   ：9/7/2019
@Desc   ：
"""

from helper import *
from model.Series import Series
from utils import my_logger as logger, wechat_logger


def creat_series_symlink(file_path, se_info, name_from_db, debug=False):
	season = se_info[1:3]
	folder = os.path.split(file_path)[0]
	filename = os.path.split(file_path)[1]

	if '/Anime' in folder:
		new_folder_path = config.symbolic_link_folder_path + "/Anime/" + name_from_db
	else:
		new_folder_path = config.symbolic_link_folder_path + "/Series/" + name_from_db
	season_folder_path = new_folder_path + "/Season " + season
	symbolic_path = season_folder_path + '/' + se_info + os.path.splitext(filename)[1]

	if not debug:
		make_dir(config.symbolic_link_folder_path)
		make_dir(config.symbolic_link_folder_path + "/Series")
		make_dir(new_folder_path)
		make_dir(season_folder_path)

		if os.path.islink(symbolic_path):
			msg_code = 'code5'
			msg = "Symbolic Link Already Exist.\n"
			logger(msg + 'Filename: [{}], Symbolic Link: [{}].'.format(filename, symbolic_path))
			info = dict(
				status='Error',
				msg_code=msg_code,
				filename=filename,
				name_from_db=name_from_db,
				season=se_info,
			)
			return info
		else:
			os.symlink(file_path, symbolic_path)
			# add info to db
			s = Series.new(dict(
				file_path=file_path,
				symbolic_path=symbolic_path
			))
			s.save()
			msg_code = 'code6'
			msg = 'Symbolic Link Build Successfully!\n'
			logger(msg + 'Filename: [{}], Symbolic Link: [{}].'.format(filename, symbolic_path))
			info = dict(
				status='Success',
				msg_code=msg_code,
				filename=filename,
				name_from_db=name_from_db,
				season=se_info,
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
				season=se_info,
			)
			return info
		else:
			s = Series.new(dict(
				file_path=file_path,
				symbolic_path=symbolic_path
			))
			s.save()
			msg_code = 'code6'
			msg = 'Debug: Symbolic Link Build Successfully!'
			logger('{} File: [{}].'.format(msg, filename))
			info = dict(
				status='Success',
				msg_code=msg_code,
				filename=filename,
				name_from_db=name_from_db,
				season=se_info,
			)
			return info


def add_info_to_result(info, result_list):
	for el in result_list:
		if el.get('name_from_db') == info.get('name_from_db') and el.get('season') == info.get('season'):
			el['episode'] += info['episode']
			break


def handle_series_all(file_path_list, debug=False):
	temp = ''
	name_from_db = ''
	result_list = []
	skipped_folder = []
	for file_path in file_path_list:
		filename = os.path.split(file_path)[1]
		folder_path = os.path.split(file_path)[0]
		formatted_name = format_filename(filename, 'Series')
		logger('formatted name: {}'.format(formatted_name))

		season_info = extract_season_info(formatted_name)

		if Series.path_in_db(file_path):
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

		if season_info is None and folder_path not in skipped_folder:
			skipped_folder.append(folder_path)
			msg_code = 'code2'
			msg = 'Season info extract failed!\n'
			logger(msg + 'Skip folder: [{}].'.format(folder_path))
			info = dict(
				status='Error',
				msg_code=msg_code,
				filename=filename,
			)
			result_list.append(info)
			continue
		elif folder_path in skipped_folder:
			continue

		final_name = season_info.get('final_name')
		logger('Derived name: {}'.format(final_name))

		se_info = season_info.get('se_info')
		logger('season & episode: {}'.format(se_info))

		if final_name != temp:
			temp = final_name
			series_name = search_from_imdb(final_name, 'Series')

			if series_name is None:
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
			elif len(series_name) == 0 :
				skipped_folder.append(folder_path)
				msg_code = 'code4'
				msg = 'No data found from imdb.\n'
				logger(msg, 'Filename: [{}], Search Keyword: [{}].'.format(filename, final_name))
				info = dict(
					status='Error',
					msg_code=msg_code,
					filename=filename,
					final_name=final_name
				)
				result_list.append(info)
				continue

			name_from_db = find_most_apt(final_name, series_name)
			name_from_db = remove_illegal(name_from_db)
			logger("Most Apt: {}".format(name_from_db))

			# create path and symbolic link
			info = creat_series_symlink(file_path, se_info, name_from_db, debug=debug)
			result_list.append(info)

		else:
			info = creat_series_symlink(file_path, se_info, name_from_db, debug=debug)
			add_info_to_result(info, result_list)
	return result_list



def rename_series(file_path_list=None, file_path=None, debug=False):
	"""
	:param file_path_list:
	:param file_path:
	:param debug:
	:return: a list of dicts
	"""
	if file_path is not None:
		result_list = handle_series_all([file_path], debug=debug)
	elif file_path_list is not None:
		result_list = handle_series_all(file_path_list, debug=debug)
	else:
		wechat_logger(title='参数错误', desp='method: `rename_movie`\n`file_path_list and file_path` are both `None`\n')
		raise KeyError
	return result_list
