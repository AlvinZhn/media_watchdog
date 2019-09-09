#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author ：Alvin
@Date   ：8/27/2019
@Desc   ：
"""
import requests
import config

import logging.config


def get_target_path(info):
	final_name = info.get('final_name')
	name_from_db = info.get('name_from_db')
	season = info.get('season')
	if final_name is None and name_from_db is None:
		return ''
	elif name_from_db is None:
		return ' => {}'.format(final_name)
	elif season is not None:
		return ' => {}'.format(name_from_db + ' ' + season)
	else:
		return ' => {}'.format(name_from_db)


def generate_message(callback_info):
	series_info = callback_info.get('Series')
	movies_info = callback_info.get('Movies')

	counter = dict(
		Movies=dict(Success=0, Warning=0, Error=0),
		Series=dict(Success=0, Warning=0, Error=0)
	)

	messages = dict(
		code1={'Movies': [], 'Series': []},
		code2={'Movies': [], 'Series': []},
		code3={'Movies': [], 'Series': []},
		code4={'Movies': [], 'Series': []},
		code5={'Movies': [], 'Series': []},
		code6={'Movies': [], 'Series': []},
	)

	for el in series_info:
		status = el.get('status')
		message_code = el.get('msg_code')
		counter['Series'][status] += 1
		del el['status']
		messages[message_code]['Series'].append(el)

	for el in movies_info:
		status = el.get('status')
		message_code = el.get('msg_code')
		counter['Movies'][status] += 1
		del el['status']
		messages[message_code]['Movies'].append(el)

	series_all = sum(counter['Series'].values())
	movies_all = sum(counter['Movies'].values())

	header1 = "### 数据总览\n"
	data = ''
	if series_all != 0:
		data += "__Series:__ _{} File(s) Processed...._\n" \
				"* `Success: {} | Warning: {} | Error: {}`\n\n".format(
			series_all, counter['Series']['Success'], counter['Series']['Warning'], counter['Series']['Error']
		)
	elif movies_all != 0:
		data += "__Movies:__ _{} File(s) Processed...._\n" \
				"* `Success: {} | Warning: {} | Error: {}`\n\n".format(
			series_all, counter['Movies']['Success'], counter['Movies']['Warning'], counter['Movies']['Error']
		)
	sep = '---\n'
	header2 = "### 详细信息\n"

	info = ''
	for key in messages:
		msg = config.message_code_dict[key]
		msg_body = "__Notice:__ _{}_\n".format(msg)
		series_info = messages[key]['Series']
		movies_info = messages[key]['Movies']
		if len(series_info) != 0:
			msg_body += "###### Series\n"
			for el in series_info:
				msg_body += "* `{}{}`\n\n".format(
					el.get('filename'),
					get_target_path(el)
				)
		if len(movies_info) != 0:
			msg_body += "###### Movies\n"
			for el in series_info:
				msg_body += "* `{}{}`\n\n".format(
					el.get('filename'),
					get_target_path(el)
				)
		info += msg_body

	desp = header1 + data + header2 + sep + info
	return desp


def wechat_logger(title='', desp='', method="POST"):
	key = config.key
	try:
		if method == "GET":
			url = "https://sc.ftqq.com/{key}.send?text={text}&desp={desp}".format(
				key=key,
				text=title,
				desp=desp
			)
			return requests.get(url=url)
		if method == "POST":
			url = "https://sc.ftqq.com/{key}.send".format(key=key)
			data = {'text': title, 'desp': desp}
			return requests.post(url=url, data=data)
	except Exception:
		print('errrrooooo')


def send_to_wechat(callback_info, status):
	title = config.wechat_message_title.get(status)

	desp = generate_message(callback_info)

	wechat_logger(title=title, desp=desp)


def my_logger(*args, **kwargs):
	logging.config.fileConfig("logging.conf")
	logger = logging.getLogger(name="rotatingFileLogger")
	return logger.info(*args, **kwargs)
