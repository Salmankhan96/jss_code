from odoo import models, fields

class AircraftComponentWorkOrderLine(models.Model):
    _name = 'aircraft.component.workorder.line'
    _description = 'Work Order Task Line'

    workorder_id = fields.Many2one(
        'aircraft.component.workorder',
        string="Work Order",tracking=True
    )
    sn = fields.Integer("S/N",tracking=True)
    task_to_be_done = fields.Text(string="Task to be done",tracking=True)
    action_taken = fields.Text(string="Action Taken",tracking=True)


class AircraftType(models.Model):
    _name = 'aircraft.type'
    _description = 'Aircraft Type Master'

    name = fields.Char(string="Aircraft Type", required=True,tracking=True)
    code = fields.Char(string="Code",tracking=True)

    workorder_ids = fields.One2many(
        'aircraft.component.workorder',
        'aircraft_type_id',
        string="Work Orders",tracking=True
    )
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, tracking=True)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    workorder_operator_ids = fields.One2many(
        'aircraft.component.workorder',
        'operator_name_id',
        string="Work Orders as Operator",tracking=True
    )

    workorder_issuer_ids = fields.One2many(
        'aircraft.component.workorder',
        'issued_by_id',
        string="Work Orders Issued",tracking=True
    )

    workorder_acceptor_ids = fields.One2many(
        'aircraft.component.workorder',
        'accepted_by_id',
        string="Work Orders Accepted",tracking=True
    )