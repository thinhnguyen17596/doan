from odoo import fields, api, models
from datetime import datetime

class Report(models.Model):
	_name = "report"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	
	
	name = fields.Char(string="Tên báo cáo", readonly=True)
	room_id = fields.Many2one(string="Phòng", comodel_name="room.motel")
	description = fields.Text(string="Nội dung")
	user_name = fields.Many2one(string= "Họ tên người báo cáo", comodel_name="my.user")
	image = fields.Many2many('ir.attachment', string='Hình ảnh')
	date = fields.Datetime(string="Ngày", default=datetime.now())
	note = fields.Char(string="Chú ý")
	state = fields.Selection(selection=[('new', 'New'), ('process', 'Processing'),('success', 'Success')],
	                         default='new', string='Trạng thái')
	
	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('report') or 'New'
		return super(Report, self).create(vals)
	
	def process_report(self):
		if self.state == 'process':
			self.state = 'success'
		elif self.state == 'success':
			self.state = 'new'
		elif self.state == 'new':
			self.state = 'process'