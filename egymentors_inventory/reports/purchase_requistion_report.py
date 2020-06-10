# -*- coding: utf-8 -*-
from odoo import models, fields
import logging


_logger = logging.getLogger(__name__)

try:
	from num2words import num2words
except ImportError:
	_logger.warning("The num2words python library is not installed, amount-to-text features won't be fully available.")
	num2words = None

# Ahmed Salama Code Start ---->


class PartnerXlsx(models.AbstractModel):
	_name = 'report.egymentors_inventory.report_purchase_requisition'
	_inherit = 'report.report_xlsx.abstract'
	
	def generate_xlsx_report(self, workbook, data, partners):
		for obj in partners:
			report_name = obj.name
			# One sheet by partner
			worksheet = workbook.add_worksheet(report_name[:31])
			format_left_to_right = workbook.add_format()
			format_left_to_right.set_font_size(25)
			format_left_to_right.set_reading_order(1)
			
			format_right_to_left = workbook.add_format()
			format_right_to_left.set_font_size(25)
			format_right_to_left.set_reading_order(2)
			cell_format_right = workbook.add_format()
			cell_format_right.set_font_size(25)
			cell_format_right.set_align('right')
			cell_format_right_bold = workbook.add_format({'bold': True, 'align': 'right'})
			worksheet.right_to_left()
			worksheet.set_column('A:A', 5)
			worksheet.set_column('B:B', 50)
			worksheet.set_column('C:X', 8)
			bold = workbook.add_format({'bold': True})
			# worksheet.insert_image(0, 0, '/web/binary/company_logo;max-width=%s&amp;max-height=%s' %
			#                        (100, 45))
			row = 2
			purchase_ids = obj.purchase_ids
			# Fill Vendors Dict
			vendors_dict = []
			for order in purchase_ids:
				if any(acc for acc in order.order_line.mapped('accepted')):
					vendors_dict.append({
						'id': order.id,
						'vendor': order.partner_id.name,
						'total_after_tax': sum(l.price_total for l in
						                       order.order_line.filtered(lambda l: l.accepted))})
			
			# Print Accepted Data
			for vendor_line in vendors_dict:
				worksheet.merge_range(row, 2, row, 3, "إجمالى عرض شركه", cell_format_right_bold)
				worksheet.merge_range(row, 4, row, 5, vendor_line['vendor'], cell_format_right_bold)
				worksheet.write(row, 6, "%s %s" % (vendor_line['total_after_tax'], obj.currency_id.symbol), bold)
				amount_text = obj.currency_id.with_context({'lang': self.env.user.lang}).amount_to_text(vendor_line['total_after_tax'])
				if self.env.user.lang in ['ar', 'ar_SY', 'ar_001']:
					amount_in_words = "%s %s" % (amount_text, "فقط لا غير.")
					amount_in_words = str(amount_in_words).replace('Euros', 'يورو')
					amount_in_words = str(amount_in_words).replace('Dollars', 'دولارات')
					amount_in_words = str(amount_in_words).replace('Dollar', 'دولار')
					amount_in_words = str(amount_in_words).replace('Cents', 'سنتاً')
					amount_in_words = str(amount_in_words).replace('Cent', 'سنت')
					amount_in_words = str(amount_in_words).replace('Pound', 'جنيهاً')
					amount_in_words = str(amount_in_words).replace('Pounds', 'جنيهات')
					amount_in_words = str(amount_in_words).replace('Piastres', 'قرشاً')
				else:
					amount_in_words = "%s Only." % amount_text
				
				worksheet.merge_range(row, 7, row, 10, amount_in_words)
				row += 1
			
			# Request Data
			if obj.request_id or obj.purchase_ids:
				name = ""
				date = ''
				if obj.request_id:
					name += obj.request_id.name
					date = obj.request_id.date_request
				elif obj.request_ids:
					for request_id in obj.request_ids:
						date = request_id.date_request
						name += "%s, " % request_id.name
				worksheet.write(row, 1, "%s رقم طلب الشراء" % name, cell_format_right_bold)
				row += 1
				worksheet.write(row, 1, "%s تاريخ طلب الشراء" % str(date), cell_format_right_bold)
				row += 1
			worksheet.merge_range(row, 1, row, 3, "%s تفريغ عروض الأسعار" % obj.name, bold)
			row += 2
			cell_format_header = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter',
			                                          'border': 1, 'fg_color': '#898a8c'})
			cell_format_row = workbook.add_format({'bold': False, 'align': 'center', 'valign': 'vcenter',
			                                       'border': 1, 'fg_color': '#D7E4BC'})
			cell_format_header.set_center_across()
			col_purchase_end = len(obj.purchase_ids)*2 + 3
			worksheet.merge_range(row, 0, row, 3, 'بيانات عرض الأسعار', cell_format_header)
			worksheet.merge_range(row, 4, row, col_purchase_end, 'بيانات عروض الموردين', cell_format_header)
			row += 1
			worksheet.merge_range(row, 0, row+1, 0, 'م', cell_format_header)
			worksheet.merge_range(row, 1, row+1, 1, 'إسم الصنف', cell_format_header)
			worksheet.merge_range(row, 2, row+1, 3, 'الكميه المطلوبه', cell_format_header)
			row += 1
			# worksheet.merge_range(row, 2, row, 3, 'الكميه', cell_format_header)
			# worksheet.write(row, 2, 'الكميه', cell_format_header)
			# worksheet.write(row, 3, 'السعر', cell_format_header)
			
			# Print Headers
			for idx, order in enumerate(purchase_ids):
				col = (idx*2)+4
				supplier = order.partner_id and order.partner_id.name or ('%s المورد' % idx)
				worksheet.merge_range(row-1, col, row-1, col+1, '%s' % supplier, cell_format_header)
				# worksheet.write(row, col,  'الكميه', cell_format_header)
				# worksheet.write(row, col+1, 'السعر', cell_format_header)
				worksheet.merge_range(row, col, row, col+1, 'السعر', cell_format_header)
			row += 1
			
			# Print Lines
			first_line_row = row
			first_line_col = col_purchase_end+1
			for idx, line in enumerate(obj.line_ids):
				worksheet.write(row, 0, idx+1, cell_format_row)
				worksheet.write(row, 1, line.product_id.display_name, cell_format_row)
				worksheet.merge_range(row, 2, row, 3, line.product_qty, cell_format_row)
				# worksheet.write(row, 2, line.product_qty, cell_format_row)
				# worksheet.write(row, 3, "%s %s" % (line.price_unit, obj.currency_id.symbol), cell_format_row)
				for y, order in enumerate(purchase_ids):
					col = (y * 2) + 4
					order_line_id = order.order_line.filtered(lambda l: l.requisition_line_id.id == line.id)
					if order_line_id:
						# worksheet.write(row, col, order_line_id.product_qty, cell_format_row)
						# worksheet.write(row, col+1, "%s %s" % (order_line_id.price_unit, obj.currency_id.symbol), cell_format_row)
						worksheet.merge_range(row, col, row, col+1, "%s %s" % (order_line_id.price_unit, obj.currency_id.symbol), cell_format_row)
				row += 1
			
			# Print Accepted Lines
			total_taxes = 0.0
			total_after_taxes = 0.0
			for line_col, order in enumerate(purchase_ids):
				if order.id in [v['id'] for v in vendors_dict]:
					header_added = False
					for line_row, line in enumerate(obj.line_ids):
						accepted_line_id = order.order_line.filtered(lambda l: l.accepted and
						                                                       l.requisition_line_id.id == line.id)
						total_taxes += accepted_line_id.price_tax
						total_after_taxes += accepted_line_id.price_total
						if accepted_line_id:
							if not header_added:
								header_added = True
								supplier = order.partner_id and order.partner_id.name or ('%s المورد' % idx)
								worksheet.merge_range(first_line_row-2, first_line_col, first_line_row-2, first_line_col+1,
								                      'إجمالى عرض الشركه', cell_format_header)
								worksheet.merge_range(first_line_row-1, first_line_col, first_line_row-1, first_line_col+1,
								                      '%s' % supplier, cell_format_header)
							
							worksheet.merge_range(first_line_row+line_row, first_line_col, first_line_row+line_row, first_line_col+1,
							                      "%s %s" % (accepted_line_id.price_subtotal, obj.currency_id.symbol), cell_format_header)
					worksheet.merge_range(row, first_line_col, row, first_line_col + 1,
					                      "%s %s" % (sum(l.price_subtotal for l in
					                                     order.order_line.filtered(lambda l: l.accepted)), obj.currency_id.symbol),
					                      cell_format_header)
					worksheet.merge_range(row+1, first_line_col, row+1, first_line_col + 1,
					                      "%s %s" % (sum(l.price_tax for l in
					                                     order.order_line.filtered(lambda l: l.accepted)),
					                                 obj.currency_id.symbol),
					                      cell_format_header)
					worksheet.merge_range(row+2, first_line_col, row+2, first_line_col + 1,
					                      "%s %s" % (sum(l.price_total for l in
					                                     order.order_line.filtered(lambda l: l.accepted)),
					                                 obj.currency_id.symbol),
					                      cell_format_header)
					first_line_col += 2
			if vendors_dict:
				worksheet.merge_range(first_line_row-3, col_purchase_end+1, first_line_row-3, first_line_col-1,
				                      'بيانات العروض المقبوله', cell_format_header)
			
			# Print Total Line
			worksheet.merge_range(row, col_purchase_end, row, col_purchase_end-1, 'الإجمـالـى', cell_format_header)
			# worksheet.write(row, 2, sum(l.product_qty for l in obj.line_ids), cell_format_header)
			# worksheet.write(row, 3, "%s %s" % (sum(l.price_unit for l in obj.line_ids), obj.currency_id.symbol),
			#                 cell_format_header)
			# for y, order in enumerate(purchase_ids):
			# 	col = (y * 2) + 4
			# 	lines = order.order_line.filtered(lambda l: l.requisition_line_id.id in obj.line_ids.mapped('id'))
			# 	worksheet.write(row, col, sum(l.product_qty for l in lines), cell_format_header)
			# 	worksheet.write(row, col+1, "%s %s" % (sum(l.price_unit for l in lines), obj.currency_id.symbol),
			# 	                cell_format_header)
			row += 1
			worksheet.merge_range(row, col_purchase_end, row, col_purchase_end-1, "إجمالي الضريبه", cell_format_header)
			# worksheet.write(row, 2, "%s %s" % (total_taxes, obj.currency_id.symbol), cell_format_header)
			row += 1
			worksheet.merge_range(row, col_purchase_end, row, col_purchase_end-1, "الإجمالى بعد الضريبه", cell_format_header)
			# worksheet.write(row, 2, "%s %s" % (total_after_taxes, obj.currency_id.symbol), cell_format_header)
			
			# Print Accepted Data final data
			if vendors_dict:
				row += 2
				worksheet.merge_range(row, 0, row, 2, "رأى اللجنه الفنيه الماليه", cell_format_right_bold)
				row += 1
				for vendor_line in vendors_dict:
					worksheet.merge_range(row, 0, row, 1, " تري اللجنه إختيار العرض المقدم من  ", cell_format_right_bold)
					worksheet.write(row, 2, vendor_line['vendor'],
					                cell_format_right_bold)
					row += 1
				
				row += 2
				# Signatures
				worksheet.merge_range(row, 0, row, 1, "توقيعات اعضاء اللجنه", cell_format_right_bold)
				worksheet.merge_range(row, 5, row, 6, "رئيس اللجنه", cell_format_right_bold)
				row += 1
				worksheet.merge_range(row, 0, row, 1, "إداره المشتريات", cell_format_right_bold)
				worksheet.merge_range(row, 2, row, 3, "الشئون الفنيه", cell_format_right_bold)
				worksheet.merge_range(row, 4, row, 5, "حسابات المخزون", cell_format_right_bold)
				worksheet.merge_range(row, 6, row, 7, "قسم الشئون القانونيه", cell_format_right_bold)
				worksheet.merge_range(row, 8, row, 9, "المراجعه", cell_format_right_bold)
				worksheet.merge_range(row, 10, row, 11, "المدير المالي", cell_format_right_bold)
				worksheet.merge_range(row, 12, row, 13, "رئيس الشئون الفنيه", cell_format_right_bold)

				row += 2
				worksheet.merge_range(row, 0, row, 1, "المرفقات", cell_format_right_bold)
				row += 1
				for vendor_line in vendors_dict:
					worksheet.merge_range(row, 0, row, 1, "عرض سعر شركه  ",
					                      cell_format_right_bold)
					worksheet.write(row, 2, vendor_line['vendor'],
					                cell_format_right_bold)
					row += 1


class ResCurrencyInherit(models.Model):
	_inherit = 'res.currency'
	
	name = fields.Char(translate=True)
	currency_unit_label = fields.Char(translate=True)
	currency_submit_label = fields.Char(translate=True)
# Ahmed Salama Code End.
