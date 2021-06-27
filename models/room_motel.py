from odoo import fields, api, models


class RoomMotel(models.Model):
	_name = "room.motel"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	
	name = fields.Char(string="Tên phòng",track_visibility='always')
	phone_number = fields.Char(string="Số điện thoại", related = "id_user.phone_number")
	id_user = fields.Many2one(string="Chủ phòng", comodel_name="my.user")
	sum_user = fields.Integer(string="Tổng thành viên", compute='get_sum_user', store=True,track_visibility='always')
	user_ids = fields.Many2many(comodel_name='my.user', relation='my_user_room_motel_rel',
	                            column1='room_motel_id', column2='my_user_id', string='Người trọ',track_visibility='always')
	id_price = fields.Many2one(string="Bảng giá", comodel_name="my.price")
	color = fields.Integer()
	
	@api.depends('user_ids')
	def get_sum_user(self):
		for room in self:
			room.sum_user = len(room.user_ids)
