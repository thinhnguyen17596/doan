import xmlrpc.client

ODOO_BACKEND = 'http://localhost:8069'
ODOO_DB = 'fuji_29-6'
ODOO_USER = 'admin'
ODOO_PASS = 'admin'


class XMLRPC_API():
    def __init__(self, url, db, username='admin', password='admin'):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        common = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/common'.format(self.url))
        self.uid = common.authenticate(
            self.db, self.username, self.password, {})
        self.models = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/object'.format(self.url))
        pass

def main():
    client = XMLRPC_API(url=ODOO_BACKEND, db=ODOO_DB,
                        username=ODOO_USER, password=ODOO_PASS)

    sql = """select product_id from stock_quant
                where (company_id = '1' or company_id = '7')
        		    """
    self._cr.execute(sql)
    sotck_quant = self._cr.dictfetchall()
    for product in sotck_quant:
        obj_product = self.env['product.template'].sudo().browse(product['product_id'])
        obj_product.active = True


if __name__ == '__main__':
    main()
