from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError


class RoomMotel(models.Model):
    _name = "room.motel"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def get_user_available(self):
        user_unavailable = []
        list_user_main = self.env['room.motel'].search([]).id_user
        for user in list_user_main:
            if user.room_ids:
                user_unavailable.append(user.id)
        main_user_room_id = self.id_user.id
        if main_user_room_id:
            user_unavailable.remove(main_user_room_id)
        return [('id', 'not in', user_unavailable)]

    name = fields.Char(string="Tên phòng",
                       track_visibility='always', required=True)
    phone_number = fields.Char(string="Số điện thoại", related="id_user.phone_number")
    id_user = fields.Many2one(
        string="Chủ phòng", comodel_name="my.user")
    sum_user = fields.Integer(string="Tổng thành viên", compute='get_sum_user', store=True, track_visibility='always')
    user_ids = fields.Many2many(comodel_name='my.user', relation='my_user_room_motel_rel',
                                column1='room_motel_id', column2='my_user_id', string='Người trọ',
                                domain=get_user_available)
    id_price = fields.Many2one(string="Bảng giá", comodel_name="my.price", required=True)
    color = fields.Integer()
    image_1920 = fields.Image()
    date_start = fields.Date(string='Ngày bắt đầu hợp đồng')
    date_end = fields.Date(string='Ngày kết thúc hợp đồng')
    max_num_users = fields.Integer(string='Số lượng thành viên tối đa')


    @api.model
    def create(self, vals):
        if vals.get('user_ids'):
            list_user = vals.get('user_ids')[0][2]
            id_user = vals.get('id_user')
            list_user_main = self.env['room.motel'].search([]).id_user.ids
            if id_user in list_user_main:
                list_user_main.remove(id_user)
            for user_id in list_user:
                if user_id in list_user_main:
                    raise UserError('Bạn không thể chọn 1 chủ phòng là thành viên của 1 phòng khác!')
        return super(RoomMotel, self).create(vals)

    def write(self, values):
        if values.get('user_ids'):
            list_user = values.get('user_ids')[0][2]
            list_user_main = self.env['room.motel'].search([]).id_user.ids
            if values.get('id_user'):
                id_user = values.get('id_user')
            else:
                id_user = self.id_user.id
            if id_user in list_user_main:
                list_user_main.remove(id_user)
            for user_id in list_user:
                if user_id in list_user_main:
                    raise UserError('Bạn không thể chọn 1 chủ phòng là thành viên của 1 phòng khác!')
        return super(RoomMotel, self).write(values)


    @api.depends('user_ids')
    def get_sum_user(self):
        for room in self:
            room.sum_user = len(room.user_ids)
            if room.sum_user > room.max_num_users:
                raise UserError('Số lượng thành viên trong phòng này đã đạt tối đa!')
