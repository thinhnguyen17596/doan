import base64

from dateutil.relativedelta import relativedelta
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo import fields, api, models
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo import http
import requests
import json
import urllib3
import uuid
import hmac
import hashlib

class MyInvoice(models.Model):
	_name = "my.invoice"
	_order = 'date desc'
	_sql_constraints = [('name', 'unique(name)', 'Hoá đơn này đã tồn tại!')]
	_inherit = ['mail.thread', 'mail.activity.mixin']
	
	name = fields.Char(string="Tên hoá đơn", readonly=True)
	room_id = fields.Many2one(string="Phòng", comodel_name="room.motel", required=True)
	id_user = fields.Many2one(comodel_name="my.user", related='room_id.id_user')
	date = fields.Datetime(string="Thời gian", default=datetime.now())
	bill_electricity = fields.Integer(string="Tiền điện", compute='get_bill_electricity', store=True)
	bill_waters = fields.Integer(string="Tiền nước", compute='get_bill_waters', store=True)
	bill_room = fields.Integer(string="Tiền phòng",  compute='get_bill_room', store=True)
	bill_internet = fields.Integer(string="Tiền Internet", related="room_id.id_price.internet_price")
	total_amount = fields.Integer(string="Tổng tiền", compute='get_total_bill', store=True)
	state = fields.Selection(selection=[('unpaid', 'Chưa thanh toán'), ('paid', 'Đã thanh toán')],
	                         default='unpaid', string='Trạng thái',track_visibility='always')
	id_invoice_detail = fields.One2many(string="Chi tiết hoá đơn", comodel_name="invoice.detail",
	                                    inverse_name="id_invoice")
	bill_advance = fields.Integer(string='Tiền thêm', track_visibility='always')
	currency_id = fields.Many2one('res.currency',string = 'Đơn vị tiền tệ', default=lambda self: self.env['res.currency'].browse(23))
	is_old_invoice = fields.Boolean(string='Hoá đơn tháng trước')
	date_deadline = fields.Date(string='Hạn thanh toán' , default=lambda self: datetime.today().replace(day=1) + relativedelta(months=+1, days=+5))
	user_id = fields.Many2one(string='Liên kết tới', comodel_name='res.users')
	report_id = fields.Many2one(string='Sự cố', comodel_name='report')


	@api.onchange('report_id')
	def get_monetary_penalty(self):
		if self.report_id:
			self.bill_advance = self.report_id.monetary_penalty


	@api.depends('id_invoice_detail.total_elec')
	def get_bill_electricity(self):
		for bill in self:
			bill.bill_electricity = bill.id_invoice_detail.total_elec * bill.room_id.id_price.electricity_price
	
	@api.depends('id_invoice_detail.total_water')
	def get_bill_waters(self):
		for bill in self:
			bill.bill_waters = bill.id_invoice_detail.total_water * bill.room_id.id_price.waters_price

	@api.depends('room_id')
	def get_bill_room(self):
		for bill in self:
			bill.bill_room = bill.room_id.id_price.room_price
	
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
		if vals.get('date'):
			date = vals.get('date')
			room_id = vals.get('room_id')
			date_time_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
			list_date_invoice_old_obj = self.env['my.invoice'].search([('room_id', '=', room_id)])
			list_date_invoice_old = list_date_invoice_old_obj.mapped('date')
			for rec in list_date_invoice_old:
				if date_time_obj.year == rec.year and date_time_obj.month == rec.month:
					raise ValidationError('Bạn không thể nhiều hoá đơn cho cùng 1 tháng!')
		vals['name'] = self.env['ir.sequence'].next_by_code('my.invoice') or 'New'
		return super(MyInvoice, self).create(vals)
	
	def name_get(self):
		# name get function for the model executes automatically
		res = []
		for rec in self:
			res.append((rec.id, '%s - %s' % (rec.name, rec.room_id.name)))
		return res

	def create_payment(self):
		url = 'https://www.youtube.com/watch?v=HP2bjrt76pQ'
		if url:
			return {
				'type': 'ir.actions.act_url',
				'url': url,
				'taget': 'new',
			}
		else:
			raise ValidationError("Eo co duong dan")

	def _create_attachment_file(self, invoice_id):
		ir_values = {}
		report_template_id = self.env.ref('motel_management.report_my_invoice')._render_qweb_pdf(invoice_id)
		data_record = base64.b64encode(report_template_id[0])
		ir_values.update({
			'name': "Hoá đơn đóng tiền trọ.pdf",
			'datas': data_record,
			'store_fname': data_record,
			'type': 'binary',
			'mimetype': 'application/pdf',
		})

		if not ir_values:
			return None
		return self.env['ir.attachment'].create(ir_values)

	def cron_auto_send_email(self):
		template_id = self.env.ref('motel_management.invoice_email_template').id
		mail_template = self.env['mail.template'].browse(template_id)
		list_invoice_ids = self.env['my.invoice'].search([('state', '=', 'unpaid')])
		for invoice in list_invoice_ids:
			attachment_ids = []
			data_invoice = self._create_attachment_file(invoice.id)
			if data_invoice:
				attachment_ids.append(data_invoice.id)
			if not attachment_ids:
				continue
			mail_template.attachment_ids = ([(6, 0, attachment_ids)])
			email_values = {'email_to': invoice.room_id.id_user.user_id.partner_id.email,
							'email_from': self.env.user.email}
			mail_template.send_mail(invoice.id, email_values=email_values, force_send=True)

		return True
