from odoo import models, fields,api,_

class StoreRequisition(models.Model):
    _name = "store.requisition"
    _description = "Store Requisition"

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    customer = fields.Many2one('res.partner',"Customer")
    assy_part_no = fields.Char("Assy. Part Number")
    assy_description = fields.Char("Assy. Description")
    dated = fields.Date("Dated")
    procedure_sheet_no = fields.Char("Procedure Sheet No.")
    assy_serial_number = fields.Char("Assy. Serial Number")
    location_and_shop = fields.Char("Location / Shop")
    remarks = fields.Text("Remarks (If any)")
    form_no = fields.Char("JS/FORM No")
    issue_date = fields.Date("Initial Issue Date")
    by_issue = fields.Selection(
        selection=[
            ('workshop_manager', 'Workshop Manager'),
            ('certifting_staff', 'Certifyting Staff'),
        ],
        string="By",
        required=True,
        default='workshop_manager'
    )
    raised_by = fields.Char("Raised by (Name & Sign)")
    raised_by_signature = fields.Binary("Signature(Raised By)")
    issued_by = fields.Char("Issued by Store Person (Name & Sign)")
    issued_by_signature = fields.Binary("Signature(Issued By)")
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)

    line_ids = fields.One2many("store.requisition.line", "requisition_id", string="Line Items")

    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    zip = fields.Char(string="Zip")
    city = fields.Char(string="City")
    state_id = fields.Many2one(
        'res.country.state', string="Fed. State", domain="[('country_id.code', '=', 'IN')]"
    )
    country_id = fields.Many2one('res.country', string="Country")

    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('store.requisition') or 'New'
        record = super(StoreRequisition, self).create(vals)
        return record

    def action_store_requisition_report(self):
        print("hjk")
        return self.env.ref('jss_code.action_report_store_requisition').report_action(self)


class StoreRequisitionLine(models.Model):
    _name = "store.requisition.line"
    _description = "Store Requisition Line"

    requisition_id = fields.Many2one("store.requisition", string="Requisition Ref", ondelete="cascade")

    sn = fields.Integer("S/N")
    description = fields.Char("Description")
    part_no = fields.Many2one('product.product',"Part No.")
    qty_requested = fields.Float("Qty Req.")
    qty_issued = fields.Float("Qty Issued")
    release_no = fields.Char("Release Note. / COC/GDN No. with Date")
    batch_no = fields.Char("Batch No.")
    serial_no = fields.Char("S/N (if any)")
    us_item_sn = fields.Char("US Item Returned S/N")
    us_qty_returned = fields.Float("Qty Returned")
