from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class WorkshopProductLine(models.Model):
    _name = 'workshop.product.line'
    _inherit = ['mail.thread', 'access.permission.mixin']
    _description = 'Workshop Product Line'

    register_id = fields.Many2one('workshop.register', string='Workshop Register', ondelete='cascade',tracking=True)
    product_id = fields.Many2one('product.product', string='Product', required=True,tracking=True)
    name = fields.Char(string='Description',tracking=True)
    quantity = fields.Float(string='Quantity', default=1.0,tracking=True)

    current_date = fields.Datetime(string="Current Date", default=fields.Datetime.now, readonly=True,tracking=True)
    doc_current_date = fields.Datetime(string="Current Date",compute="_compute_relative_date")
    manual_date = fields.Datetime(string="Manual Date",tracking=True)
    doc_manual_date = fields.Datetime(string="Manual Date",compute="_compute_relative_date")
    signature = fields.Many2one('res.users', string="Signature",tracking=True)

    handover_to = fields.Char(string='Handover To',tracking=True)
    task_to_be_done = fields.Char(string='Task To Be Done',tracking=True)
    sign_by = fields.Many2one('res.users', string="Sign By",tracking=True)
    challan_no = fields.Char(string='Challan No.',tracking=True)
    remarks = fields.Text(string='Remarks',tracking=True)

    so_po_ro_no = fields.Char(string='So Po Ro No.',tracking=True)
    
    def _compute_relative_date(self):
        for rec in self:
            if rec.current_date:
                rec.doc_current_date = rec.current_date + relativedelta(hours=3, minutes=30)
            if rec.manual_date:
                rec.doc_manual_date = rec.manual_date + relativedelta(hours=3, minutes=30)
    
    @api.model
    def default_get(self, fields_list):
        res = super(WorkshopProductLine, self).default_get(fields_list)
        return res