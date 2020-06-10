# -*- coding: utf-8 -*-
# from odoo import http


# class EgymentorsProductCode(http.Controller):
#     @http.route('/egymentors_product_code/egymentors_product_code/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/egymentors_product_code/egymentors_product_code/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('egymentors_product_code.listing', {
#             'root': '/egymentors_product_code/egymentors_product_code',
#             'objects': http.request.env['egymentors_product_code.egymentors_product_code'].search([]),
#         })

#     @http.route('/egymentors_product_code/egymentors_product_code/objects/<model("egymentors_product_code.egymentors_product_code"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('egymentors_product_code.object', {
#             'object': obj
#         })
