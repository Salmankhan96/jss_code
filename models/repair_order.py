from odoo import models, fields, api
from datetime import datetime, timedelta

class RepairOrder(models.Model):
    _name = 'repair.jss'
    _inherit = ['access.permission.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Repair Jss'
    _rec_name = 'custom_refer'

    custom_refer = fields.Char(
        string='Form Tracking Number',
        required=True,
        copy=False,
        readonly=False,
        default='New',
        tracking=True
    )

    work_order_reference = fields.Many2one(
        'aircraft.component.workorder',
        string='W/O No.',
        required=True,tracking=True
    )

    user_id = fields.Many2one(
        'res.users',
        string='Assigned New person',tracking=True,domain=lambda self: [('groups_id', 'in', self.env.ref('jss_code.group_certifying_staff').ids)]
    )
    signature = fields.Binary(string='Signature', attachment=True)


    current_date = fields.Date(
        string='Date',
        default=fields.Date.context_today,tracking=True
    )
    doc_issued_date = fields.Datetime(string="Date",compute="_compute_issued_date",store=True)


    custom_remark = fields.Text(
        string='Remarks',tracking=True
    )

    move_ids = fields.One2many(
        'repair.jss.line',
        'order_id',
        string='Order Lines',tracking=True
    )
    
    has_edit_request = fields.Boolean(
        string="Edit Requested",
        compute='_compute_has_edit_request',
        store=False
    )
    has_download_request = fields.Boolean(
        string="Download Requested",
        compute='_compute_has_download_request',
        store=False
    )
    is_engineer = fields.Boolean(compute='_compute_is_engineer', store=False)
    can_show_request_edit = fields.Boolean(compute='_compute_permission_visibility', store=False)
    can_show_grant_edit = fields.Boolean(compute='_compute_permission_visibility', store=False)
    can_show_request_download = fields.Boolean(compute='_compute_permission_visibility', store=False)
    can_show_grant_download = fields.Boolean(compute='_compute_permission_visibility', store=False)
    can_download_pdf = fields.Boolean(compute='_compute_permission_visibility', store=False)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, tracking=True)

    can_edit_signature = fields.Boolean(compute='_compute_signature_permissions')

    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    zip = fields.Char(string="Zip")
    city = fields.Char(string="City")
    state_id = fields.Many2one(
        'res.country.state', string="Fed. State", domain="[('country_id.code', '=', 'IN')]"
    )
    country_id = fields.Many2one('res.country', string="Country")

    @api.depends('signature')
    def _compute_issued_date(self):
        for rec in self:
            if rec.signature:
                rec.doc_issued_date = datetime.now() + timedelta(hours=5, minutes=30)
            else:
                rec.doc_issued_date = False

    @api.depends('user_id')
    def _compute_signature_permissions(self):
        current_user = self.env.user
        for rec in self:
            rec.can_edit_signature = (rec.user_id == current_user)


    @api.depends('has_edit_request', 'has_download_request', 'is_engineer') # Added dependencies
    def _compute_permission_visibility(self):
        for record in self:
            user = self.env.user
            is_engineer_or_superuser = user.has_group('jss_code.group_engineer') or user.has_group('jss_code.group_super_user')

            # Check for active edit permission for the current user
            has_active_edit_permission = bool(self.env['access.permission.line'].search([
                ('form_model', '=', self._name),
                ('form_record_id', '=', record.id),
                ('permission_type', '=', 'edit'),
                ('user_id', '=', user.id),
                ('granted', '=', True),
                ('used', '=', False)
            ], limit=1))

            # Check for active download permission for the current user
            has_active_download_permission = bool(self.env['access.permission.line'].search([
                ('form_model', '=', self._name),
                ('form_record_id', '=', record.id),
                ('permission_type', '=', 'download'),
                ('user_id', '=', user.id),
                ('granted', '=', True),
                ('used', '=', False)
            ], limit=1))

            # Visibility for "Request Edit" button
            # Show if not engineer/superuser AND no pending request AND no active permission
            record.can_show_request_edit = not is_engineer_or_superuser and not record.has_edit_request and not has_active_edit_permission

            # Visibility for "Grant Edit" button (for engineers)
            # Show if engineer AND there's a pending edit request
            record.can_show_grant_edit = record.is_engineer and record.has_edit_request

            # Visibility for "Request Download" button
            # Show if not engineer/superuser AND no pending request AND no active permission
            record.can_show_request_download = not is_engineer_or_superuser and not record.has_download_request and not has_active_download_permission

            # Visibility for "Grant Download" button (for engineers)
            # Show if engineer AND there's a pending download request
            record.can_show_grant_download = record.is_engineer and record.has_download_request

            # Visibility for "Download PDF" button
            # Show if engineer/superuser OR has active download permission
            record.can_download_pdf = is_engineer_or_superuser or has_active_download_permission

    def _compute_has_edit_request(self):
        for record in self:
            record.has_edit_request = bool(self.env['access.permission.line'].search([
                ('form_model', '=', self._name),
                ('form_record_id', '=', record.id),
                ('permission_type', '=', 'edit'),
                ('used', '=', False)
            ], limit=1))

    def _compute_has_download_request(self):
        for record in self:
            record.has_download_request = bool(self.env['access.permission.line'].search([
                ('form_model', '=', self._name),
                ('form_record_id', '=', record.id),
                ('permission_type', '=', 'download'),
                ('used', '=', False)
            ], limit=1))


    @api.depends('create_uid')
    def _compute_is_engineer(self):
        engineer_group = self.env.ref('jss_code.group_engineer')
        for rec in self:
            rec.is_engineer = engineer_group in self.env.user.groups_id

    def write(self, vals):
        self.check_user_has_permission('edit')
        res = super().write(vals)
        Perm = self.env['access.permission.line']
        permission = Perm.search([
            ('form_model', '=', self._name),
            ('form_record_id', '=', self.id),
            ('user_id', '=', self.env.user.id),
            ('permission_type', '=', 'edit'),
            ('granted', '=', True),
            ('used', '=', False),
        ], limit=1)

        if permission:
            permission.sudo().write({'used': True})
            self.message_post(body=f"Permission to edit marked as used by {self.env.user.name} for form tracking number {self.custom_refer}.")
        return res

    def create(self, vals):
        if vals.get('custom_refer', 'New') == 'New':
            today = datetime.today()
            year = today.strftime('%Y')
            month = today.strftime('%m')

            count = self.search_count([
                ('create_date', '>=', f'{year}-{month}-01'),
                ('create_date', '<', f'{year}-{int(month) + 1:02}-01' if int(month) < 12 else f'{int(year) + 1}-01-01')
            ]) + 1

            sequence = f"JSS/DGCA/{count}/{year}-{month}"
            vals['custom_refer'] = sequence

        return super().create(vals)

    def action_generate_pdf(self):
        self.ensure_one()
        self.check_user_has_permission('download')
        res = self.env.ref('jss_code.action_report_repair_order').report_action(self)
        Perm = self.env['access.permission.line']
        permission = Perm.search([
            ('form_model', '=', self._name),
            ('form_record_id', '=', self.id),
            ('user_id', '=', self.env.user.id),
            ('permission_type', '=', 'download'),
            ('granted', '=', True),
            ('used', '=', False),
        ], limit=1)

        if permission:
            permission.sudo().write({'used': True})
            self.message_post(body=f"Permission to download marked as used by {self.env.user.name} for form tracking number {self.custom_refer}.")
        return res


    def action_request_edit(self):
        self.ensure_one()
        engineers = self.env['res.users'].search([
            ('groups_id', 'in', self.env.ref('jss_code.group_engineer').id)
        ])
        existing_request = self.env['access.permission.line'].search([
            ('form_model', '=', self._name),
            ('form_record_id', '=', self.id),
            ('permission_type', '=', 'edit'),
            ('user_id', '=', self.env.user.id),
            ('used', '=', False)
        ], limit=1)
        if existing_request:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Request Already Submitted',
                    'message': 'You have an active pending edit request for this record.',
                    'type': 'warning',
                    'sticky': False,
                }
            }

        self.env['access.permission.line'].sudo().create({
            'form_model': self._name,
            'form_record_id': self.id,
            'permission_type': 'edit',
            'user_id': self.env.user.id,
        })
        self.sudo().message_post(body="🛠️ Edit request submitted.", partner_ids=engineers.mapped('partner_id').ids)

        # template = self.env.ref('jss.email_template_permission_request')
        # ctx = {
        #     'default_model': self._name,
        #     'default_res_id': self.id,
        #     'ctx_permission_type': 'Edit',
        #     'user': self.env.user,
        #     'engineer_users': engineers,
        #     'record_name': self.name,
        #     'record_url': self.get_form_url(),
        # }
        # template.with_context(ctx).sudo().send_mail(self.id, force_send=True)

        # Trigger recompute of visibility fields after a request is made
        self.invalidate_recordset(['can_show_request_edit', 'can_show_grant_edit', 'has_edit_request'])

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Request Submitted',
                'message': 'Your request to edit has been sent to the Engineer.',
                'type': 'success',
                'sticky': False,
            }
        }


    def action_request_download(self):
        self.ensure_one()
        engineers = self.env['res.users'].search([
            ('groups_id', 'in', self.env.ref('jss_code.group_engineer').id)
        ])
        existing_request = self.env['access.permission.line'].search([
            ('form_model', '=', self._name),
            ('form_record_id', '=', self.id),
            ('permission_type', '=', 'download'),
            ('user_id', '=', self.env.user.id),
            ('used', '=', False)
        ], limit=1)
        if existing_request:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Request Already Submitted',
                    'message': 'You have an active pending download request for this record.',
                    'type': 'warning',
                    'sticky': False,
                }
            }

        self.env['access.permission.line'].sudo().create({
            'form_model': self._name,
            'form_record_id': self.id,
            'permission_type': 'download',
            'user_id': self.env.user.id,
        })
        self.message_post(body="📥 Download request submitted.", partner_ids=engineers.mapped('partner_id').ids)

        # template = self.env.ref('jss.email_template_permission_request')
        # ctx = {
        #     'default_model': self._name,
        #     'default_res_id': self.id,
        #     'ctx_permission_type': 'Download',
        #     'user': self.env.user,
        #     'engineer_users': engineers,
        #     'record_name': self.name,
        #     'record_url': self.get_form_url(),
        # }
        # template.with_context(ctx).sudo().send_mail(self.id, force_send=True)

        # Trigger recompute of visibility fields after a request is made
        self.invalidate_recordset(['can_show_request_download', 'can_show_grant_download', 'has_download_request'])

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Request Submitted',
                'message': 'Your request to download has been sent to the Engineer.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_grant_edit_permission(self):
        self.ensure_one()
        engineers = self.env['res.users'].search([
            ('groups_id', 'in', self.env.ref('jss_code.group_engineer').id)
        ])
        pending_request = self.env['access.permission.line'].search([
            ('form_model', '=', self._name),
            ('form_record_id', '=', self.id),
            ('permission_type', '=', 'edit'),
            ('used', '=', False),
            ('granted', '=', False)
        ], limit=1)

        if not pending_request:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Pending Request',
                    'message': 'There is no pending edit request for this record to grant.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        pending_request.sudo().write({
            'granted': True,
            'granted_by_id': self.env.user.id,
            'granted_on': fields.Datetime.now()
        })
        self.sudo().message_post(body=f"🛠️ Edit request permitted for {pending_request.user_id.name} by Engineer.", partner_ids=engineers.ids)
        # model_name = self._name
        # model_line_name = model_name + '.line'
        # model_id = self.env['ir.model'].search([('model','in',(model_name,model_line_name))]).ids
        # user_planning = self.env['res.groups'].search([('name', '=', 'Planning')], limit=1)
        # user_workshop_manager = self.env['res.groups'].search([('name', '=', 'Workshop Manager')], limit=1)
        # # pending_request.user_id.groups_id
        # user_to_permit = False
        # for i in pending_request.user_id.groups_id.ids:
        #     if user_planning.id == i:
        #         user_to_permit = user_planning.id
        # access_model = self.env['ir.model.access'].search([('model_id','in',model_id),('group_id','=',user_to_permit)])
        # if access_model:
        #     access_model.write({'perm_write': True})
        self.invalidate_recordset(['can_show_request_edit', 'can_show_grant_edit', 'has_edit_request'])

        return {
            'name': 'Grant Edit Permission',
            'type': 'ir.actions.act_window',
            'res_model': 'access.permission.line',
            'view_mode': 'form',
            'res_id': pending_request.id, # Open the existing permission line for review
            'context': {
                'form_view_ref': 'jss_code.access_permission_line_view_form_grant',
                'default_form_model': self._name,
                'default_form_record_id': self.id,
                'default_permission_type': 'edit',
                'default_user_id': pending_request.user_id.id,
                'default_granted_by_id': self.env.user.id,
                'hide_user_selection': True,
                'hide_permission_type_selection': True,
            },
            'target': 'new'
        }

    def action_grant_download_permission(self):
        self.ensure_one()
        engineers = self.env['res.users'].search([
            ('groups_id', 'in', self.env.ref('jss_code.group_engineer').id)
        ])
        pending_request = self.env['access.permission.line'].search([
            ('form_model', '=', self._name),
            ('form_record_id', '=', self.id),
            ('permission_type', '=', 'download'),
            ('used', '=', False),
            ('granted', '=', False)
        ], limit=1)

        if not pending_request:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Pending Request',
                    'message': 'There is no pending download request for this record to grant.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        pending_request.sudo().write({
            'granted': True,
            'granted_by_id': self.env.user.id,
            'granted_on': fields.Datetime.now()
        })
        self.sudo().message_post(body=f"🛠️ Download request permitted by Engineer for {pending_request.user_id.name}.", partner_ids=engineers.ids)
        self.invalidate_recordset(
            ['can_show_request_download', 'can_show_grant_download', 'has_download_request', 'can_download_pdf'])

        return {
            'name': 'Grant Download Permission',
            'type': 'ir.actions.act_window',
            'res_model': 'access.permission.line',
            'view_mode': 'form',
            'res_id': pending_request.id, # Open the existing permission line for review
            'context': {
                'form_view_ref': 'jss_code.access_permission_line_view_form_grant',
                'default_form_model': self._name,
                'default_form_record_id': self.id,
                'default_permission_type': 'download',
                'default_user_id': pending_request.user_id.id,
                'hide_user_selection': True,
                'hide_permission_type_selection': True,
                'current_record_id': self.id,
                'current_model_name': self._name,
            },
            'target': 'new'
        }

    def get_form_url(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"

    # @api.model
    # def create(self, vals):
    #     if vals.get('custom_refer', 'New') == 'New':
    #         today = datetime.today()
    #         year = today.strftime('%Y')
    #         month = today.strftime('%m')
    #
    #         count = self.search_count([
    #             ('create_date', '>=', f'{year}-{month}-01'),
    #             ('create_date', '<', f'{year}-{int(month) + 1:02}-01' if int(month) < 12 else f'{int(year) + 1}-01-01')
    #         ]) + 1
    #
    #         sequence = f"JSS/DGCA/{count}/{year}-{month}"
    #         vals['custom_refer'] = sequence
    #
    #     return super(RepairOrder, self).create(vals)
    #
    # def print_repair_report(self):
    #     return self.env.ref('jss.action_report_repair_order').report_action(self)


class RepairOrderLine(models.Model):
    _name = 'repair.jss.line'
    _description = 'Repair Jss Line'

    order_id = fields.Many2one(
        'repair.jss',
        string='Repair Order Reference',
        ondelete='cascade',
        required=True,
        tracking=True
    )

    sequence = fields.Integer(
        string='Serial No.',
        readonly=True,
        default=0,tracking=True
    )

    product_id = fields.Many2one(
        'product.product',
        string='Part',
        required=True,tracking=True
    )

    part_no = fields.Char(
        string='Part No.',
        related='product_id.default_code',
        default='0000',
        store=True,
        readonly=True,tracking=True
    )

    product_uom_qty = fields.Float(
        string='Quantity',
        default='0',
        required=True,tracking=True
    )

    other = fields.Char(
        string='Serial/Batch No.',
        default='N/A',
        readonly=False,tracking=True
    )

    status_work = fields.Selection([
        ('repaired', 'Repaired'),
        ('inspected_tested', 'Inspected & Tested'),
        ('overhauled', 'Overhauled'),
        ('modification', 'Modification'),
    ], string="Status Work", required=True,tracking=True)

    def get_status_work_display(self):
        """Returns the display label for the current status_work value."""
        return dict(self._fields['status_work'].selection).get(self.status_work, '')

    @api.model
    def create(self, vals):
        if 'order_id' in vals:
            order = self.env['repair.jss'].browse(vals['order_id'])
            vals['sequence'] = len(order.move_ids) + 1
        return super(RepairOrderLine, self).create(vals)
