# coding: utf-8
import odoo
import logging
from odoo import http
import json
class ApiProduct(http.Controller):

    @http.route('/products_detail', type='json', auth='public', methods=['GET'])
    def search_products_detail(self, **kw):
        print('vao dung')
        content = []
        product_ids = http.request.env['product.product'].sudo().search([],limit=30)
        for product in product_ids:
            content.append({
                'id': product.id,
                'name': product.name,
                'active': product.active,
                'uom': product.uom_id.name,
                'barcode': product.barcode,
                'price_unit': product.lst_price,
            })
        return {"res" : content}

    @http.route('/products_detail/<id>/delete', type='http', auth='public', methods=['DELETE'],csrf=False)
    def delete_products_detail(self, id, **kw):
        print('vao dung')
        http.request.env['res.partner'].sudo().search([('id', '=', int(id))]).unlink()
        return {"Succsess"}
