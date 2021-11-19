from odoo import fields, api, models
from datetime import datetime

class Report(models.Model):
	_name = "report"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	
	
	name = fields.Char(string="Tên báo cáo", readonly=True)
	room_id = fields.Many2one(
		string="Phòng", comodel_name="room.motel", required=True)
	description = fields.Text(string="Nội dung", required=True)
	user_name = fields.Many2one(string="Chủ phòng", comodel_name="my.user", related='room_id.id_user')
	image = fields.Many2many('ir.attachment', string='Video hoặc hình ảnh khác')
	image2 = fields.Image(string='Hình ảnh')
	date = fields.Datetime(string="Ngày", default=datetime.now())
	note = fields.Char(string="Chú ý")
	state = fields.Selection(selection=[('new', 'Mới'), ('process', 'Đang xử lý'),('success', 'Đã xử lý')],
	                         default='new', string='Trạng thái')
	monetary_penalty = fields.Float(string='Tiền phạt', default=0)
	
	@api.model
	def create(self, vals):
		sequence = self.env['ir.sequence'].next_by_code('report') or 'New'
		room_name = self.env['room.motel'].browse(vals.get('room_id')).name
		vals['name'] = sequence + ' ' +  room_name
		return super(Report, self).create(vals)
	
	def process_report(self):
		if self.state == 'process':
			self.state = 'success'
		elif self.state == 'success':
			self.state = 'new'
		elif self.state == 'new':
			self.state = 'process'
