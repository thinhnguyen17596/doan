from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError
import datetime


class InvoiceDetail(models.Model):
	_name = "invoice.detail"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_sql_constraints = [('name', 'unique(name)', 'Chi tiết hoá đơn này đã tồn tại!')]
	
	name = fields.Char(string="Tên chi tiết hoá đơn", readonly=True)
	num_elec_begin_month = fields.Integer(string="Số điện đầu tháng")
	num_elec_end_month = fields.Integer(string="Số điện cuối tháng", required=True)
	total_elec = fields.Integer(string="Tổng số điện", compute='get_total_elec', store=True)
	num_water_begin_month = fields.Integer(string="Số nước đầu tháng")
	num_water_end_month = fields.Integer(string="Số nước cuối tháng", required=True)
	total_water = fields.Integer(string="Tổng số nước", compute='get_total_water', store=True)
	id_invoice = fields.Many2one(string="ID hoá đơn", comodel_name='my.invoice', ondelete='cascade')
	is_old_invoice = fields.Integer(string='num',compute='check_old_invoice')
	
	@api.depends("num_elec_begin_month", 'num_elec_end_month')
	def get_total_elec(self):
		for bill in self:
			bill.total_elec = bill.num_elec_end_month - bill.num_elec_begin_month
	
	@api.depends("num_water_begin_month", 'num_water_end_month')
	def get_total_water(self):
		for bill in self:
			bill.total_water = bill.num_water_end_month - bill.num_water_begin_month
	
	@api.onchange('num_elec_end_month','num_water_end_month')
	def check_old_invoice(self):
		if self.num_elec_begin_month != 0 or self.num_water_begin_month:
			self.is_old_invoice = 1
		else:
			self.is_old_invoice = 0
	
	
	
	@api.onchange('num_water_end_month', 'num_elec_end_month')
	def _get_num_elec_end_month(self):
		room_id = int(self.id_invoice.room_id)
		self.env.cr.execute(f'''SELECT name,room_id,id FROM my_invoice where room_id = {room_id} ORDER BY date DESC''')
		list_invoice = self.env.cr.fetchall()
		print('phòng', room_id)
		print("danh sách invoice", list_invoice)
		
		if len(list_invoice) >= 1:
			id_record_latest = list_invoice[0]
			print('Record mới nhất', id_record_latest)
			invoice_detail_id = int(id_record_latest[2])
			print('id record mới nhất', invoice_detail_id)
			ls_invoice_detail = self.env['invoice.detail'].search([('id_invoice', '=', invoice_detail_id)])
			print("Danh sách các chi tiết hoá đơn", ls_invoice_detail)
			if self.is_old_invoice == 0:
				if len(ls_invoice_detail) >= 1:
					id_late_invoice_detail = int(ls_invoice_detail[0])
					print('id chi tiết hoá đơn mới nhất', id_late_invoice_detail)
					obj_invoice_detail = self.env['invoice.detail'].browse(id_late_invoice_detail)
					self.num_elec_begin_month = obj_invoice_detail.num_elec_end_month
					self.num_water_begin_month = obj_invoice_detail.num_water_end_month
					print(obj_invoice_detail.num_water_end_month)
					print(obj_invoice_detail.num_elec_end_month)
				else:
					pass
		
		else:
			pass
	
	@api.constrains('num_water_end_month', 'num_water_begin_month')
	def check_num_water(self):
		if self.num_water_end_month < self.num_water_begin_month:
			raise ValidationError('Bạn đang nhập số nước bị sai!')
	
	@api.constrains('num_elec_begin_month', 'num_elec_end_month')
	def check_num_elec(self):
		if self.num_elec_end_month < self.num_elec_begin_month:
			raise ValidationError('Bạn đang nhập số điện bị sai!')
	
	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('invoice.detail') or 'New'
		return super(InvoiceDetail, self).create(vals)
	
	def name_get(self):
		# name get function for the model executes automatically
		res = []
		for rec in self:
			res.append((rec.id, '%s - %s' % (rec.name, rec.id_invoice.room_id.name)))
		return res
	
	# @api.depends('num_water_end_month', 'num_elec_end_month')
	# def get_name_invoice_detail(self):
	# 	name = ''
	# 	date_time_now = datetime.datetime.now()
	# 	year = date_time_now.year
	# 	month = date_time_now.month
	# 	# name_room = str(self.id_invoice.room_id.name)
	# 	name += str(year) + '/' + str(month) + '/'
	# 	for i in self:
	# 		i.name = name
