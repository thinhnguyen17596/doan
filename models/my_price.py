from odoo import fields, api, models
from datetime import datetime

class MyPrice(models.Model):
	_name = "my.price"
	
	name = fields.Char(string="Tên số nhà")
	date = fields.Datetime(string="Thời gian lập" ,default=datetime.now())
	electricity_price = fields.Integer(string="Giá điện / 1 số")
	waters_price = fields.Integer(string="Giá nước / 1 khối")
	room_price = fields.Integer(string="Giá phòng")
	internet_price = fields.Integer(string="Giá Internet / 1 phòng")
	

