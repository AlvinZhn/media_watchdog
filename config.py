#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author ：Alvin
@Date   ：8/26/2019
@Desc   ：
"""

media_folder_path = '/home/alvin/Media'
symbolic_link_folder_path = '/home/alvin/Link'

key = ''

watched_patterns = [
	'*.part',
]

exclude_folder = [
	'Finished',
	'Others',
	'temp',
	'Seeding',
	'BDMV',
	'CD',
	'CERTIFICATE',
]

allowed_extn = [
	'.mp4', '.mkv', '.avi', '.m2ts', '.ts', '.str', '.ass'
]

suffix_list = [
	# Region
	".JPN",
	# Resolution
	".1080P", ".720P", ".2160P", ".BD1080P", ".HD1080P", ".HD4K", ".UHD",
	# Encoder
	".X264", ".X265", ".H264", ".H265",
	# Foramt
	".HDTV", ".BLU-RAY", ".DTS-HD", ".WEB-DL", ".WEBRIP", ".HEVC", ".BLURAY", ".AVC", ".REMUX"
]

redundant = [
	'UNCUT',
	'EXTENDED',
]

wechat_message_title = dict(
	init='文件监控服务初始化完成',
	check='数据库比对完成',
	moved='新文件下载完成'
)

message_code_dict = dict(
	code1='File path exist in db.\n',
	code2='Season info extract failed!\n',
	code3='Error occurred while searching\n',
	code4='No data found from imdb.\n',
	code5="Symbolic Link Already Exist.\n",
	code6='Symbolic Link Build Successfully!\n',
)
