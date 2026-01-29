# -*- coding: utf-8 -*-
from email.policy import default
from lxml import etree
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class LogisticsUnserviceItem(models.Model):
    _name = 'logistics.unservice.item'
    _description = 'Logistics Service Item'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="GRN",
        required=True, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))

    servicability = fields.Char(string='Servicability')

    customer_id = fields.Many2one('res.partner', string="Customer", required=True)
    grn_date = fields.Date(string="Unserviceable Date")

    order_type = fields.Selection([
        ('ro', 'RO'),
        ('po', 'PO'),
        ('so', 'SO')
    ], string="Order Type")

    order_value = fields.Char(string="Order Value")
    order_date = fields.Date(string="Order Date")

    identification_tag = fields.Binary(string="Identification Tag")

    unservice_item_line_ids = fields.One2many(
        'logistics.unservice.item.line', 'logistics_id', string="Product Lines"
    )

    stage = fields.Selection([
        ('new', 'New'),
        ('prepare_goods', 'Prepare Goods'),
        ('handover', 'Hand Over to Planning')
    ], string="Stage", default='new', tracking=True)

    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    zip = fields.Char(string="Zip")
    city = fields.Char(string="City")
    state_id = fields.Many2one(
        'res.country.state', string="Fed. State", domain="[('country_id.code', '=', 'IN')]"
    )
    country_id = fields.Many2one('res.country', string="Country")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, tracking=True)

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super(LogisticsUnserviceItem, self).get_view(view_id=view_id, view_type=view_type, **options)

        if view_type == 'form' and res.get('arch'):
            arch = etree.XML(res['arch'])

            user_in_group = self.env.user.has_group('jss_code.group_store')

            if not user_in_group:
                for node in arch.xpath("//field[@name='serviceable_date']"):
                    node.set('readonly', '1')

            res['arch'] = etree.tostring(arch, encoding='unicode')

        return res

    def write(self, vals):
        if 'grn_date' in vals and not (
                self.env.user.has_group('jss_code.group_store') or
                self.env.user.has_group('base.group_system')
        ):
            raise ValidationError("Only Store users or Administrators can update Serviceable Date.")
        return super().write(vals)

    @api.onchange('order_type')
    def _onchange_order_type(self):
        """Generate different sequence based on order_type"""
        if self.order_type:
            sequence_code = f"order.sequence.{self.order_type}"
            self.order_value = self.env['ir.sequence'].next_by_code(sequence_code) or "New"

    def action_handover(self):
        """Switch stage to Handover to Planning"""
        for rec in self:
            if rec.name == 'New':  # only assign if still "New"
                rec.name = self.env['ir.sequence'].next_by_code('logistics.unservice.item') or '/'
            rec.stage = 'handover'

    def action_goods(self):
        """Switch stage to Prepare Goods"""
        for rec in self:
            rec.stage = 'prepare_goods'

    def action_back_to_new(self):
        """Switch stage back to New"""
        for rec in self:
            rec.stage = 'new'

    def print_grn_pdf(self):
        return self.env.ref('jss_code.action_report_logistics_grn').report_action(self)

    procedure_sheet = fields.Selection([
        ('overall', 'Overall'),
        ('service', 'Service'),
        ('fabrication', 'Fabrication'),
        ('repair', 'Repair'),
        ('inspection', 'Inspection'),
        ('tested', 'Tested'),
        ('tc', 'T/C'),
        ('dry_cleaning', 'Dry Cleaning'),
        ('cleaning', 'Cleaning'),
        ('refilling', 'Refilling'),
        ('hst', 'HST'),
        ('others', 'Others'),
    ], string="Procedure Sheet")

    procedure_sheet_other = fields.Char(string="Procedure Sheet (Other)")

    received_by = fields.Selection([
        ('customer', 'Customer'),
        ('jss_ampl', 'JSS AMPL'),
    ], string="Received By")

    remarks = fields.Char(string='Remarks')
    signature = fields.Binary(string="Signature")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

class LogisticsUnserviceItemLine(models.Model):
    _name = 'logistics.unservice.item.line'
    _description = 'GRN Product Line'

    logistics_id = fields.Many2one('logistics.unservice.item', string="GRN Reference", ondelete="cascade")

    product_id = fields.Many2one('product.product', string="Part No.", required=True)

    identifier_value = fields.Char(string="Identifier Value")

    description = fields.Text(string="Description")
    aircraft_type = fields.Char(string="Aircraft Type")
    registration_no = fields.Char(string="Registration No.")
    quantity = fields.Float(string="Quantity", default=1.0)
    product_uom = fields.Many2one('uom.uom',string="Unit")
    expiry = fields.Date(string="Expiry")
    location_id = fields.Char(string="Location")
    condition_remarks = fields.Char(string="Condition/Remarks")