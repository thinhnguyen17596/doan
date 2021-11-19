from odoo import fields, api, models


class MyUser(models.Model):
    _name = "my.user"
    _rec_name = "user_name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    user_name = fields.Char(string="Tên", requied=True, tracking=True)
    image_1920 = fields.Image()
    email = fields.Char(string="Email", required=True, tracking=True)
    dob = fields.Date(string="Ngày sinh", required=True, tracking=True)
    phone_number = fields.Char(
        string="Số điện thoại", required=True, tracking=True)
    identity = fields.Char(string="CMDN/CCCD", required=True, tracking=True)
    room_ids = fields.Many2many(string="Phòng", relation='my_user_room_motel_rel',
                                column1='my_user_id', column2='room_motel_id', comodel_name="room.motel", track_visibility="onchange")
    user_id = fields.Many2one(string='Liên kết tới', comodel_name='res.users')
    contract = fields.Binary(string="Hợp đồng")

    @api.model
    def create(self, vals):
        name = vals.get('user_name', False)
        if name:
            vals['user_name'] = name.title()
        res = super(MyUser, self).create(vals)
        data = {
                'email': res.email,
                'groups_id': [(6, 0, [12,1])],
                'name': res.user_name,
                'login': res.email,
                'password': '1234',
            }
        res_user = self.env['res.users'].create(data)
        res.user_id = res_user

        return res

    def write(self, vals):
        res = super(MyUser, self).write(vals)
        if self.user_id:
            self.user_id.write({
                                'login': self.email,
                                'email': self.email,
                                'name': self.user_name
                                })

        return res



    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #     user_unavailable = []
    #     list_user_main = self.env['room.motel'].search([]).id_user
    #     for user in list_user_main:
    #         if user.room_ids:
    #             user_unavailable.append(user.id)
    #     domain = [('id', 'not in', user_unavailable)]
    #
    #     return super(MyUser, self).search_read(domain=domain, fields=fields, offset=offset,
    #                                              limit=limit, order=order)
 
