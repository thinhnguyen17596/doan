# -*- coding: utf-8 -*-

{
    'name': 'Motel management',
    'version': '1.0',
    'summary': 'Motel management',
    'sequence': 0,
    'description': """
		Quản lý nhà trọ
    """,
	'author': 'Nguyen Huu Thinh',
    'category': 'Others',
    'website': 'https://www.facebook.com/thinh.nguyenhuu.357',
    'depends': ['mail'],
    'data': [
        'security/security_data.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/main_menu.xml',
        'views/my_user_view.xml',
        'views/report_view.xml',
        'views/room_motel_view.xml',
        'views/my_price_view.xml',
        'views/invoice_view.xml',
        'views/invoice_detail_view.xml',
        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
