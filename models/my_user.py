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
    is_manager = fields.Boolean(compute="_check_user_group")

    @api.model
    def create(self, vals):
        name = vals.get('user_name', False)
        if name:
            vals['user_name'] = name.title()
        record = super(MyUser, self).create(vals)
        return record

    @api.onchange('user_name')
    def _check_user_group(self):
        if self.env.user.has_group('motel_management.group_motel_manager'):
            self.is_manager = 1
 
