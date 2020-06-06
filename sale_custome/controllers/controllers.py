# -*- coding: utf-8 -*-
# from odoo import http


# class SaleCustome(http.Controller):
#     @http.route('/sale_custome/sale_custome/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_custome/sale_custome/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_custome.listing', {
#             'root': '/sale_custome/sale_custome',
#             'objects': http.request.env['sale_custome.sale_custome'].search([]),
#         })

#     @http.route('/sale_custome/sale_custome/objects/<model("sale_custome.sale_custome"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_custome.object', {
#             'object': obj
#         })
