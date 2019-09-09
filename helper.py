#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author ：Alvin
@Date   ：8/30/2019
@Desc   ：
"""
import os
import re

from imdb import IMDb, IMDbDataAccessError
from similarity.damerau import Damerau

import config


def make_dir(folder_path):
	try:
		os.mkdir(folder_path)
	except FileExistsError:
		pass


def is_chinese(strings):
	for c in strings:
		if '\u4e00' <= c <= '\u9fa5':
			return True
	return False


def remove_chinese(temp):
	temp_list = list(filter(None, temp.split('.')))
	new_list = []
	for strings in temp_list:
		if not is_chinese(strings):
			new_list.append(strings)
	name = '.'.join(new_list)
	if name[0] == '.':
		name = name.replace('.', '', 1)
	return name


def remove_square_bracket(file):
	square_brackets = re.findall('[\[]+(.*?)[\]]', file)
	for el in square_brackets:
		file = file.replace('[' + el + ']', '')
	return file.strip()


def replace_redundant(file):
	file = file.replace('-', ' ').replace('_', ' ')
	file = file.split('.' + file.split('.')[-1], 1)[0]
	return file.strip()


def remove_bracket(file, media_type):
	if media_type == 'Series':
		brackets = re.findall('[(]+(.*?)[)]', file)
		for el in brackets:
			file = file.replace('(' + el + ')', '')
	else:
		file = file.replace('(', ' ').replace(')', ' ')
	return file.strip()


def format_filename(file, media_type):
	temp = remove_bracket(file, media_type)
	temp = remove_chinese(temp)
	rest = remove_square_bracket(temp).upper()
	suffix = config.suffix_list
	a = 0
	for el in suffix:
		if rest.find(el) > 0 and (a == 0 or a > rest.find(el)):
			a = rest.find(el)
	if a != 0:
		rest = rest[:a].replace(".", " ")
	else:
		rest = rest.replace(".", " ")
	rest = replace_redundant(rest)
	return rest


def get_movie_result(s_result):
	result = []
	for el in s_result:
		if el['kind'] in ['movie', 'tv movie', 'video movie']:
			str2 = el['title']
			try:
				year_str = el['year']
			except KeyError:
				year_str = "----"
			result.append(str2 + " (" + str(year_str) + ")")
	return result


def get_series_result(s_result):
	result = []
	for el in s_result:
		if el['kind'] == "tv miniseries" or el['kind'] == "tv series":
			str2 = el['title']
			result.append(str2)
	return result


def search_from_imdb(str21, media_type):
	result_list = []
	ia = IMDb()
	try:
		print("Searching {} now...".format(str21))
		s_result = ia.search_movie(str21)
	except IMDbDataAccessError:
		return None
	if media_type == 'Movie':
		result_list = get_movie_result(s_result)
	elif media_type == 'Series':
		result_list = get_series_result(s_result)
	return result_list


def find_most_apt(name, results):
	damerau = Damerau()
	deg = []
	for el in results:
		if name.upper() == el.upper():
			return el
		else:
			deg.append(damerau.distance(name.upper(), el.upper()))
	indd = int(deg.index(min(deg)))
	mostapt = results[indd]
	return mostapt


def remove_illegal(strings):
	illegal_str = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
	for el in illegal_str:
		strings = strings.replace(el, "")
	return strings.strip()


def find_name(rest):
	input_string = rest.replace(' X ', 'X', 1)
	filtered_list = filter(None, re.split(r'(\dX\d)', input_string))
	for element in filtered_list:
		element = element.replace('-', ' ')
		element = element.replace('.', ' ')
		return str(element.strip())


def find_det(rest):
	input_string = rest.replace(' X ', 'X', 1)
	filtered_list = filter(None, re.split(r'(\dX\d\d)', input_string))
	i = 0
	for element in filtered_list:
		det = element
		det = det.replace('.', ' ')
		det = det.replace('-', ' ')
		det = det.strip()
		if i == 1:
			return str(det)
		i = i + 1


def find_season(rest):
	det = find_det(rest)
	season = det.split('X')[0]
	return str(season)


def find_episode(rest):
	det = find_det(rest)
	episode = det.split('X')[1]
	return str(episode)


def add_zero(input_string):
	if int(input_string) < 10:
		return str('0' + str(int(input_string)))
	return input_string


def has_x(filename):
	return bool(
		re.search(r'\dx\d', filename) or
		re.search(r'\d x \d', filename) or
		re.search(r'\dX\d', filename) or
		re.search(r'\d X \d', filename)
	)


def has_se(input_string):
	return bool(
		re.search(r'S\d\dE\d\d', input_string) or
		re.search(r'S\dE\d\d', input_string) or
		re.search(r's\d\de\d\d', input_string) or
		re.search(r's\de\d\d', input_string)
	)


def has_sexxx(input_string):
	return bool(
		re.search(r'S\d\dE\d\d\d', input_string) or
		re.search(r'S\dE\d\d\d', input_string) or
		re.search(r's\d\de\d\d\d', input_string) or
		re.search(r's\de\d\d\d', input_string)
	)


def has_sep(input_string):
	return bool(
		re.search(r'S\d\dEP\d\d', input_string) or
		re.search(r'S\dEP\d\d', input_string) or
		re.search(r's\d\dep\d\d', input_string) or
		re.search(r's\dep\d\d', input_string)
	)


def has_ep(input_string):
	return bool(
		re.search(r'E\d\d', input_string) or
		re.search(r'EP\d\d', input_string) or
		re.search(r'e\d\d', input_string) or
		re.search(r'ep\d\d', input_string)
	)


def get_se(word):
	se_info = None
	if has_se(word):
		se_info = word
	elif has_ep(word):
		se_info = 'S01' + word
	if has_sep(word):
		se_info = word
	return se_info


def extract_season_info(formatted_filename):
	# Specifically written for'x' type Files
	if has_x(formatted_filename):
		final_name = find_name(formatted_filename)
		season = find_season(formatted_filename)
		episode = add_zero(find_episode(formatted_filename))
		se_info = "S" + add_zero(season) + "E" + episode

	# Specifically written for 'S__E__' or 'E__' or 'EP__' type Files
	elif has_se(formatted_filename) or has_ep(formatted_filename):
		final_name = ""
		se_info = ''
		words = formatted_filename.split()
		for index, word in enumerate(words):
			info = get_se(word)
			if info is not None and index != 0:
				se_info = info
				break
			elif info is not None and index == 0:
				se_info = info
				continue
			else:
				final_name = final_name + word + " "

	# no season info in file name
	else:
		# todo
		return None
	return dict(
		final_name=final_name,
		se_info=se_info
	)


def get_file_path_list(folder_path):
	file_path_list = []
	for root, dirs, files in os.walk(folder_path, topdown=True):
		dirs[:] = [d for d in dirs if d not in config.exclude_folder]
		for filename in files:
			if ('.' + str(filename).split('.')[-1]) in config.allowed_extn:
				file_path_list.append(os.path.join(root, filename))
	return file_path_list
