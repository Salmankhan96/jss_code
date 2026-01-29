from odoo import models, fields,api,_
from odoo.exceptions import ValidationError
from lxml import etree

class LogisticsServiceItem(models.Model):
    _name = 'logistics.service.item'
    _description = 'Serviceable Items for Servicing or Sale'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Reference",
        required=True, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))
    serviceable_date = fields.Date(string="Serviceable Date")

    source_from = fields.Selection([
        ('customer', 'Customer'),
        ('jss_ampl', 'JSS AMPL')
    ], string="Received From", required=True, tracking=True,default='jss_ampl')

    delivery_challan = fields.Char(string="Delivery Challan / Invoice No.")
    delivery_date = fields.Date(string="Delivery Challan / Invoice Date")
    partner_id = fields.Many2one('res.partner',string="Customer")
    rfq_ref = fields.Char(string="RFQ Reference")
    quotation_ref = fields.Char(string="Quotation Reference")
    po_number = fields.Char(string="PO Number")
    po_date = fields.Date(string="PO Date")
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)
    supplied_by = fields.Char(string="Supplied By")
    certificate_no = fields.Char(string="Certificate No.")
    certificate_date = fields.Date(string="Certificate Date")
    physical_condition = fields.Char(string="Physical Condition")
    self_life = fields.Char(string="Self-Life")
    accessories = fields.Char(string="Accessories (If Any)")

    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    zip = fields.Char(string="Zip")
    city = fields.Char(string="City")
    state_id = fields.Many2one(
        'res.country.state', string="Fed. State", domain="[('country_id.code', '=', 'IN')]"
    )
    country_id = fields.Many2one('res.country',string="Country")

    # Notebook for check/enter
    line_ids = fields.One2many('logistics.service.item.line', 'service_item_id', string="Check/Enter Lines")


    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super(LogisticsServiceItem, self).get_view(view_id=view_id, view_type=view_type, **options)

        if view_type == 'form' and res.get('arch'):
            arch = etree.XML(res['arch'])

            user_in_group = self.env.user.has_group('jss_code.group_store')

            if not user_in_group:
                for node in arch.xpath("//field[@name='grn_date']"):
                    node.set('readonly', '1')

            res['arch'] = etree.tostring(arch, encoding='unicode')

        return res


    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('logistics.service.item') or 'New'
        record = super(LogisticsServiceItem, self).create(vals)
        return record

    def write(self, vals):
        if 'serviceable_date' in vals and not (
                self.env.user.has_group('jss_code.group_store') or
                self.env.user.has_group('base.group_system')
        ):
            raise ValidationError("Only Store users or Administrators can update Serviceable Date.")
        return super().write(vals)


class LogisticsServiceItemLine(models.Model):
    _name = 'logistics.service.item.line'
    _description = 'Service Item Line Details'

    service_item_id = fields.Many2one('logistics.service.item', string="Service Item", ondelete="cascade")

    serial_no = fields.Char(string="S.No")
    serial_no2 = fields.Char(string="S.No")
    batch_no = fields.Char(string="Batch No.")
    lot_no = fields.Char(string="Lot No.")
    description = fields.Text(string="Description")
    part_no = fields.Many2one('product.product', string="Part Number", required=True)
    qty_demanded = fields.Float(string="Qty Demanded")
    qty_received = fields.Float(string="Qty Received")
    qty_rejected = fields.Float(string="Qty Rejected")







