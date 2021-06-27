from odoo import fields, api, models


class MyUser(models.Model):
	_name = "my.user"
	_rec_name = "user_name"
	
	user_name = fields.Char(string="Tên", requied=True)
	image = fields.Binary(attachment=True)
	email = fields.Char(string="Email")
	dob = fields.Date(string="Ngày sinh")
	phone_number = fields.Char(string="Số điện thoại")
	identity = fields.Char(string="CMDN/CCCD")
	room_ids = fields.Many2many(string="Phòng", relation='my_user_room_motel_rel',
	                            column1='my_user_id', column2='room_motel_id',comodel_name="room.motel")
	user_id = fields.Many2one(string='Liên kết tới', comodel_name='res.users')
	is_manager = fields.Boolean(compute="_check_user_group")

	@api.onchange('user_name')
	def _check_user_group(self):
		if self.env.user.has_group('motel_management.group_motel_manager'):
			self.is_manager = 1
 