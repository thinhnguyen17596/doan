from odoo import fields, api, models
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo import http
import requests

class MyInvoice(models.Model):
	_name = "my.invoice"
	_order = 'date desc'
	_sql_constraints = [('name', 'unique(name)', 'Hoá đơn này đã tồn tại!')]
	_inherit = ['mail.thread', 'mail.activity.mixin']
	
	name = fields.Char(string="Tên hoá đơn", readonly=True)
	room_id = fields.Many2one(string="Phòng", comodel_name="room.motel", required=True)
	date = fields.Datetime(string="Thời gian", default=datetime.now())
	bill_electricity = fields.Integer(string="Tiền điện", compute='get_bill_electricity', store=True)
	bill_waters = fields.Integer(string="Tiền nước", compute='get_bill_waters', store=True)
	bill_room = fields.Integer(string="Tiền phòng", related="room_id.id_price.room_price")
	bill_internet = fields.Integer(string="Tiền Internet", related="room_id.id_price.internet_price")
	total_amount = fields.Integer(string="Tổng tiền", compute='get_total_bill', store=True)
	state = fields.Selection(selection=[('unpaid', 'Chưa thanh toán'), ('paid', 'Đã thanh toán')],
	                         default='unpaid', string='Trạng thái',track_visibility='always')
	id_invoice_detail = fields.One2many(string="Chi tiết hoá đơn", comodel_name="invoice.detail",
	                                    inverse_name="id_invoice")
	currency_id = fields.Many2one('res.currency',string = 'Đơn vị tiền tệ', default=lambda self: self.env['res.currency'].browse(23))
	is_old_invoice = fields.Boolean(string='Hoá đơn tháng trước')
	
	@api.onchange('room_id','date')
	def get_old_invoice(self):
		old_invoice = self.env['my.invoice'].sudo().search([('room_id' ,"=", self.room_id.id),('date','<',self.date)],limit=1)
		print(old_invoice)
		if old_invoice:
			old_invoice.id_invoice_detail.num_elec_end_month = self.id_invoice_detail.num_elec_begin_month
			old_invoice.id_invoice_detail.num_water_end_month = self.id_invoice_detail.num_water_begin_month
		else:
			pass
	
	@api.depends('id_invoice_detail.total_elec')
	def get_bill_electricity(self):
		for bill in self:
			bill.bill_electricity = bill.id_invoice_detail.total_elec * bill.room_id.id_price.electricity_price
	
	@api.depends('id_invoice_detail.total_water')
	def get_bill_waters(self):
		for bill in self:
			bill.bill_waters = bill.id_invoice_detail.total_water * bill.room_id.id_price.waters_price
	
	@api.depends('bill_electricity', 'bill_waters', 'bill_room', 'bill_internet')
	def get_total_bill(self):
		for bill in self:
			bill.total_amount = bill.bill_electricity + bill.bill_waters + bill.bill_room + bill.bill_internet
	
	def process_invoice(self):
		if self.state == 'unpaid':
			self.state = 'paid'
		elif self.state == 'paid':
			self.state = 'unpaid'
	
	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('my.invoice') or 'New'
		return super(MyInvoice, self).create(vals)
	
	def name_get(self):
		# name get function for the model executes automatically
		res = []
		for rec in self:
			res.append((rec.id, '%s - %s' % (rec.name, rec.room_id.name)))
		return res
	
	def alo(self):
		print('alo')
		base_url = self.env['ir.config_parameter'].get_param('web.base.url')
		print(base_url)
		print(requests.Request)
	
	
	
	
	# url = 'http://rptdesign'
		# if url:
		# 	return {
		# 		'type': 'ir.actions.act_url',
		# 		'url': url,
		# 		'taget': 'new',
		# 	}
		# else:
		# 	raise ConnectionRefusedError("Eo co duong dan")

# @api.depends('room_id')
	# def get_name_invoice(self):
	# 	name = ''
	# 	date_time_now = datetime.now()
	# 	year = date_time_now.year
	# 	month = date_time_now.month
	# 	# name_room = str(self.room_id.name)
	# 	name += str(year) + '/' + str(month) + '/'
	# 	for i in self:
	# 		i.name = name