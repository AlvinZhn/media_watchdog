#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author ：Alvin
@Date   ：8/27/2019
@Desc   ：
"""
from rename_movie import rename_movie
from rename_series import rename_series



def rename_all(file_path_dict=None, debug=False):
	"""
	:param file_path_dict: a dict of media type to media file path(str)
	:return: a dict of lists, contain all status info
	"""
	callback_info = dict(
		Movies=[],
		Series=[],
	)

	movie_path_list = file_path_dict.get('Movie')
	series_path_list = file_path_dict.get('Series')

	if movie_path_list is not None:
		movie_result_list = rename_movie(file_path_list=movie_path_list, debug=debug)
		callback_info['Movies'] += movie_result_list

	if series_path_list is not None:
		series_result_list = rename_series(file_path_list=series_path_list, debug=debug)
		callback_info['Series'] += series_result_list

	return callback_info
