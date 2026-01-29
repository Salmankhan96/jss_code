from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccessPermissionLine(models.Model):
    _name = 'access.permission.line'
    _description = 'Access Permission Line'
    _rec_name = 'form_model'

    form_model = fields.Char(string="Model Name", required=True)
    form_record_id = fields.Integer(string="Record ID", required=True)

    user_id = fields.Many2one('res.users', string="User", required=True)
    permission_type = fields.Selection([
        ('edit', 'Edit'),
        ('download', 'Download')
    ], string="Permission Type", required=True)

    granted = fields.Boolean(string="Permission Granted", default=False)
    granted_by_id = fields.Many2one('res.users', string="Granted By", default=lambda self: self.env.uid)
    granted_on = fields.Datetime(string="Granted On", default=fields.Datetime.now)

    used = fields.Boolean(string="Permission Used", default=False)

    @api.model
    def create(self, vals):
        # When creating, if 'granted' is True, set granted_by_id and granted_on
        if vals.get('granted'):
            vals['granted_by_id'] = self.env.user.id
            vals['granted_on'] = fields.Datetime.now()
        return super().create(vals)

    def write(self, vals):
        # If 'granted' is set to True, and it was previously False, record who granted and when.
        if 'granted' in vals and vals['granted'] and not self.granted:
            vals['granted_by_id'] = self.env.user.id
            vals['granted_on'] = fields.Datetime.now()
        res = super().write(vals)
        return res