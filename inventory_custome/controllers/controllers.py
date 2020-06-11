# -*- coding: utf-8 -*-
# from odoo import http


# class InventoryCustome(http.Controller):
#     @http.route('/inventory_custome/inventory_custome/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inventory_custome/inventory_custome/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('inventory_custome.listing', {
#             'root': '/inventory_custome/inventory_custome',
#             'objects': http.request.env['inventory_custome.inventory_custome'].search([]),
#         })

#     @http.route('/inventory_custome/inventory_custome/objects/<model("inventory_custome.inventory_custome"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inventory_custome.object', {
#             'object': obj
#         })
