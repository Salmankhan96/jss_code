from odoo import models, fields, api
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class AircraftComponentWorkOrder(models.Model):
    _name = 'aircraft.component.workorder'
    _inherit = ['access.permission.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Aircraft Component Work Order'
    _rec_name = 'operator_work_order_no'

    aircraft_type_id = fields.Many2one(
        'aircraft.type',
        string="Aircraft Type",
        required=True,
        ondelete='restrict',tracking=True
    )
    issued_by_id = fields.Many2one(
        'res.users',
        string="Issued By",tracking=True,
        domain=lambda self: [('groups_id', 'in', [self.env.ref('jss_code.group_workshop_manager').id,self.env.ref('jss_code.group_deputy_workshop_manager').id])]
    )
    accepted_by_id = fields.Many2one(
        'res.users',
        string="Accepted By",tracking=True,
        domain=lambda self: [('groups_id', 'in', self.env.ref('jss_code.group_certifying_staff').ids)]
    )
    operator_name_id = fields.Many2one(
        'res.users',
        string="Operator Name",tracking=True
    )
    operator_name = fields.Char(string="Operator Name",tracking=True)
    aircraft_type = fields.Char(string="Aircraft Type",tracking=True)
    operator_work_order_no = fields.Char(string="Operator Work Order No",tracking=True)
    operator_issue_date = fields.Datetime(string="Operator Issue Date",tracking=True)
    doc_operator_issue_date = fields.Datetime(string="Operator Issue Date",compute="_compute_relative_issue_date")
    amo_work_order_no = fields.Char(string="AMO Work Order No",tracking=True, readonly=True, copy=False)
    amo_issue_date = fields.Datetime(string="AMO Issue Date",tracking=True)
    doc_amo_issue_date = fields.Datetime(string="AMO Issue Date", compute="_compute_relative_issue_date")
    # issued_by_name = fields.Char(string="Issued By Name",tracking=True,)
    # accepted_by_name = fields.Char(string="Accepted By Name",tracking=True,)
    job_allocation_serial_no = fields.Char(string="Job Allocation Serial No",tracking=True, readonly=True, copy=False)
    requisition_slip_serial_no = fields.Char(string="Requisition Slip Serial No",tracking=True, readonly=True, copy=False)
    # work_order_completed_by = fields.Char(string="Work Order Completed By",tracking=True)
    issued_by_signature = fields.Binary("Signature(Issued By)")
    doc_issued_by_date = fields.Datetime(string="Issued by Date",compute="_compute_issued_by_date",store=True)
    accepted_by_signature = fields.Binary("Signature(Accepted By)")
    doc_accepted_by_date = fields.Datetime(string="Accepted by Date",compute="_compute_accepted_by_date",store=True)
    remarks = fields.Text(string="Remarks",tracking=True)

    workshop_manager = fields.Many2one('res.users', string='Authorized Person (Workshop Manager)',tracking=True,domain=lambda self: [('groups_id', 'in', [self.env.ref('jss_code.group_workshop_manager').id,self.env.ref('jss_code.group_deputy_workshop_manager').id])])
    workshop_date = fields.Datetime(string='Datetime (Workshop Manager)',tracking=True)
    doc_workshop_date = fields.Datetime(string='Datetime (Workshop Manager)',compute="_compute_relative_issue_date")
    workshop_signature = fields.Binary(string='Signature (Workshop Manager)')

    quality_manager = fields.Many2one('res.users', string='Quality Manager',tracking=True,domain=lambda self: [('groups_id', 'in', [self.env.ref('jss_code.group_quality').id,self.env.ref('jss_code.group_deputy_quality_manager').id])])
    quality_date = fields.Datetime(string='Datetime (Quality Manager)',tracking=True)
    doc_quality_date = fields.Datetime(string="Datetime (Quality Manager)",compute="_compute_relative_issue_date")
    quality_signature = fields.Binary(string='Signature (Quality Manager)')

    auth_number = fields.Binary(string='Authorization Number / Stamp')
    auth_date_sign = fields.Datetime(string='Datetime (Auth person)',tracking=True)
    doc_auth_date_sign = fields.Datetime(string="Datetime (Auth person)",compute="_compute_relative_issue_date")
    auth_person_name = fields.Many2one('res.users', string='Auth Person Name',tracking=True,domain=lambda self: [('groups_id', 'in', self.env.ref('jss_code.group_certifying_staff').ids)])

    line_ids = fields.One2many(
        'aircraft.component.workorder.line',
        'workorder_id',
        string="Tasks",tracking=True
    )

    form_no2 = fields.Char(string="Form No. 2",tracking=True)

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company,tracking=True)

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

    can_edit_auth_signature = fields.Boolean(compute='_compute_signature_permissions')
    can_edit_quality_signature = fields.Boolean(compute='_compute_signature_permissions')
    can_edit_workshop_signature = fields.Boolean(compute='_compute_signature_permissions')
    can_edit_issued_by_signature = fields.Boolean(compute='_compute_signature_permissions')
    can_edit_accepted_by_signature = fields.Boolean(compute='_compute_signature_permissions')

    @api.depends('issued_by_signature')
    def _compute_issued_by_date(self):
        for rec in self:
            if rec.issued_by_signature:
                rec.doc_issued_by_date = datetime.now() + timedelta(hours=5, minutes=30)
            else:
                rec.doc_issued_by_date = False

    @api.depends('accepted_by_signature')
    def _compute_accepted_by_date(self):
        for rec in self:
            if rec.accepted_by_signature:
                rec.doc_accepted_by_date = datetime.now() + timedelta(hours=5, minutes=30)
            else:
                rec.doc_accepted_by_date = False

    def _compute_relative_issue_date(self):
        for rec in self:
            if rec.operator_issue_date:
                rec.doc_operator_issue_date = rec.operator_issue_date + relativedelta(hours=3, minutes=30)
            if rec.amo_issue_date:
                rec.doc_amo_issue_date = rec.amo_issue_date + relativedelta(hours=3, minutes=30)
            if rec.workshop_date:
                rec.doc_workshop_date = rec.workshop_date + relativedelta(hours=5, minutes=30)
            if rec.quality_date:
                rec.doc_quality_date = rec.quality_date + relativedelta(hours=5, minutes=30)
            if rec.auth_date_sign:
                rec.doc_auth_date_sign = rec.auth_date_sign + relativedelta(hours=3, minutes=30)

    @api.depends('quality_manager','auth_person_name','workshop_manager','issued_by_id','accepted_by_id')
    def _compute_signature_permissions(self):
        current_user = self.env.user
        for rec in self:
            rec.can_edit_auth_signature = (rec.auth_person_name == current_user)
            rec.can_edit_quality_signature = (rec.quality_manager == current_user)
            rec.can_edit_workshop_signature = (rec.workshop_manager == current_user)
            rec.can_edit_issued_by_signature = (rec.issued_by_id == current_user)
            rec.can_edit_accepted_by_signature = (rec.accepted_by_id == current_user)

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

    @api.onchange('workshop_signature')
    def _onchange_workshop_signature(self):
        if self.workshop_signature:
            self.workshop_date = fields.Datetime.now()

    @api.onchange('quality_signature')
    def _onchange_quality_signature(self):
        if self.quality_signature:
            self.quality_date = fields.Datetime.now()

    @api.onchange('auth_number')
    def _onchange_auth_fields(self):
        if self.auth_number:
            self.auth_date_sign = fields.Datetime.now()


    @api.depends('create_uid')
    def _compute_is_engineer(self):
        engineer_group = self.env.ref('jss_code.group_engineer')
        for rec in self:
            rec.is_engineer = engineer_group in self.env.user.groups_id

    def get_financial_year(self):
        today = date.today()
        year = today.year
        if today.month < 4:
            return f"{year - 1 % 100:02d}-{year % 100:02d}"
        else:
            return f"{year % 100:02d}-{(year + 1) % 100:02d}"

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
            self.message_post(body=f"Permission to edit marked as used by {self.env.user.name} for operator work order no: {self.operator_work_order_no}.")
        return res

    def create(self, vals_list):
        fiscal_year = self.get_financial_year()

        if not vals_list.get('amo_work_order_no'):
            seq = self.env['ir.sequence'].next_by_code('jss_code.amo.work.order') or '/'
            vals_list['amo_work_order_no'] = f"JSS/AMO/{fiscal_year}/{seq}"

        if not vals_list.get('job_allocation_serial_no'):
            seq = self.env['ir.sequence'].next_by_code('jss_code.job.allocation') or '/'
            vals_list['job_allocation_serial_no'] = f"JSS/JA/{fiscal_year}/{seq}"

        if not vals_list.get('requisition_slip_serial_no'):
            seq = self.env['ir.sequence'].next_by_code('jss_code.requisition.slip') or '/'
            vals_list['requisition_slip_serial_no'] = f"JSS/RS/{fiscal_year}/{seq}"
        if self.env.user.has_group('jss_code.group_super_user') or self.env.user.has_group('jss_code.group_engineer'):
            return super().create(vals_list)
        return super().create(vals_list)

    def action_generate_pdf(self):
        self.ensure_one()
        self.check_user_has_permission('download')
        res = self.env.ref('jss_code.action_report_aircraft_workorder_pdf').report_action(self)
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
            self.message_post(body=f"Permission to download marked as used by {self.env.user.name} for operator work order no: {self.operator_work_order_no}.")
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

    # def action_print_pdf(self):
    #     return self.env.ref('jss.action_report_aircraft_workorder_pdf').report_action(self)


class JobAllocationForm(models.Model):
    _name = 'job.allocation.form'
    _inherit = ['access.permission.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Job Allocation Form'
    _rec_name = 'serial_no'

    workorder_no = fields.Many2one(
        'aircraft.component.workorder',
        string='W/O No.',
        required=True,tracking=True
    )
    date = fields.Datetime("Date",tracking=True,default=fields.Datetime.now)
    doc_date = fields.Datetime("Date",compute='_compute_related_date')
    certified_name =  fields.Many2one('res.users', string='Name of Person',tracking=True,domain=lambda self: [('groups_id', 'in', [self.env.ref('jss_code.group_workshop_manager').id,self.env.ref('jss_code.group_deputy_workshop_manager').id,self.env.ref('jss_code.group_certifying_staff').id])])
    certified_signature = fields.Binary("Signature")
    line_ids = fields.One2many('job.allocation.line', 'form_id', string="Allocation Lines",tracking=True)
    serial_no = fields.Char(related='workorder_no.job_allocation_serial_no',string='Serial No',tracking=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company,tracking=True)
    date_sign = fields.Datetime(string='Signed Datetime', tracking=True)
    doc_date_sign = fields.Datetime(string='Signed Datetime',compute='_compute_related_date')
    role_field = fields.Char('User Role')

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

    can_edit_signature = fields.Boolean(compute='_compute_signature_permissions')
    
    def _compute_related_date(self):
        for rec in self:
            if rec.date_sign:
                rec.doc_date_sign = rec.date_sign + relativedelta(hours=3, minutes=30)
            if rec.date:
                rec.doc_date = rec.date + relativedelta(hours=3, minutes=30)

    @api.onchange('certified_signature','certified_name')
    def _onchange_sign_fields(self):
        if self.certified_signature or self.certified_name:
            self.date_sign = fields.Datetime.now()
            self.role_field ='certifying_staff' if self.certified_name.has_group('jss_code.group_certifying_staff') else 'workshop_manager'

    @api.depends('certified_name')
    def _compute_signature_permissions(self):
        current_user = self.env.user
        for rec in self:
            rec.can_edit_signature = (rec.certified_name == current_user)

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
            self.message_post(body=f"Permission to edit marked as used by {self.env.user.name} for record {self._name}.")
        return res

    @api.model
    def create(self, vals):
        if self.env.user.has_group('jss_code.group_super_user') or self.env.user.has_group('jss_code.group_engineer') or self.env.user.has_group('jss_code.group_workshop_manager') or self.env.user.has_group('jss_code.group_deputy_workshop_manager') or self.env.user.has_group('jss_code.group_certifying_staff'):
            return super().create(vals)

    def action_generate_pdf(self):
        self.ensure_one()
        self.check_user_has_permission('download')
        res = self.env.ref('jss_code.action_report_job_allocation_form_pdf').report_action(self)
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
            self.message_post(body=f"Permission to download marked as used by {self.env.user.name} for record {self.name}.")
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



class JobAllocationLine(models.Model):
    _name = 'job.allocation.line'
    _description = 'Job Allocation Line'

    form_id = fields.Many2one('job.allocation.form', string="Form",tracking=True)
    sn = fields.Integer("S/N",tracking=True)
    person_name = fields.Char("Name of Person",tracking=True)
    designation = fields.Char("Designation",tracking=True)
    signature = fields.Binary("Signature")
    remarks = fields.Text("Remarks",tracking=True)




class DeliveryChallan(models.Model):
    _name = 'delivery.challan'
    _inherit = ['access.permission.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Delivery Challan'
    _rec_name = 'challan_no'

    challan_no = fields.Char(string="Challan No",tracking=True,readonly=True,copy=False)
    date = fields.Datetime(string="Challan Date",tracking=True,default=fields.Datetime.now)
    doc_date = fields.Datetime(string="Challan Date",compute="_compute_relative_date")
    partner_id = fields.Many2one('res.partner',string="Customer Name",tracking=True)
    saleperson_id = fields.Many2one('delivery.contact.user',string="Contact Person",tracking=True)
    contact_number = fields.Char(string="Contact Number",tracking=True)
    po_so_ro_no = fields.Char(string="PO/SO/RO No.",tracking=True)
    po_so_ro_date = fields.Datetime(string="Date of PO/SO/RO",tracking=True,default=fields.Datetime.now)
    doc_po_so_ro_date = fields.Datetime(string="Date of PO/SO/RO",compute="_compute_relative_date")
    gst = fields.Char(string="GST", default="09AAECJ9966F1Z0",tracking=True)
    remarks = fields.Text(string="Remarks",tracking=True)
    created_by = fields.Many2one('res.users',string="Created By",tracking=True,default= lambda self:self.env.user)

    auth_stamp = fields.Binary(
        string="Auth Sign",
        attachment=True
    )
    auth_signature_date = fields.Datetime(
        string="Sign Date",tracking=True
    )
    doc_auth_signature_date = fields.Datetime(string="Sign Date",compute="_compute_relative_date")
    recieving = fields.Char("Recieved by",tracking=True)

    line_ids = fields.One2many('delivery.challan.line', 'challan_id', string="Line Items",tracking=True)

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
    is_super = fields.Boolean(compute='_compute_is_engineer', store=False)
    can_show_request_edit = fields.Boolean(compute='_compute_permission_visibility', store=False)
    can_show_grant_edit = fields.Boolean(compute='_compute_permission_visibility', store=False)
    can_show_request_download = fields.Boolean(compute='_compute_permission_visibility', store=False)
    can_show_grant_download = fields.Boolean(compute='_compute_permission_visibility', store=False)
    can_download_pdf = fields.Boolean(compute='_compute_permission_visibility', store=False)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, tracking=True)
    can_edit_auth_by_signature = fields.Boolean(compute='_compute_signature_permissions')

    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    zip = fields.Char(string="Zip")
    city = fields.Char(string="City")
    state_id = fields.Many2one(
        'res.country.state', string="Fed. State", domain="[('country_id.code', '=', 'IN')]"
    )
    country_id = fields.Many2one('res.country', string="Country")


    def _compute_relative_date(self):
        for rec in self:
            if rec.date:
                rec.doc_date = rec.date + relativedelta(hours=3, minutes=30)
            if rec.po_so_ro_date:
                rec.doc_po_so_ro_date = rec.po_so_ro_date + relativedelta(hours=3, minutes=30)
            if rec.auth_signature_date:
                rec.doc_auth_signature_date = rec.auth_signature_date + relativedelta(hours=3, minutes=30)

    @api.depends('created_by')
    def _compute_signature_permissions(self):
        current_user = self.env.user
        for rec in self:
            rec.can_edit_auth_by_signature = (rec.created_by == current_user)

    @api.onchange('auth_stamp')
    def _onchange_auth_stamp(self):
        if self.auth_stamp:
            self.auth_signature_date = fields.Datetime.now()

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
            record.can_show_grant_edit = (record.is_engineer or record.is_super) and record.has_edit_request

            # Visibility for "Request Download" button
            # Show if not engineer/superuser AND no pending request AND no active permission
            record.can_show_request_download = not is_engineer_or_superuser and not record.has_download_request and not has_active_download_permission

            # Visibility for "Grant Download" button (for engineers)
            # Show if engineer AND there's a pending download request
            record.can_show_grant_download = (record.is_engineer or record.is_super) and record.has_download_request

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
        super_group = self.env.ref('jss_code.group_super_user')
        for rec in self:
            rec.is_engineer = engineer_group in self.env.user.groups_id
            rec.is_super = super_group in self.env.user.groups_id

    def get_financial_year(self):
        today = date.today()
        year = today.year
        if today.month < 4:
            return f"{year - 1 % 100:02d}-{year % 100:02d}"
        else:
            return f"{year % 100:02d}-{(year + 1) % 100:02d}"

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
            self.message_post(body=f"Permission to edit marked as used by {self.env.user.name} for record {self.challan_no}.")
        return res

    @api.model
    def create(self, vals_list):
        # vals_list['created_by']= self.env.user.id
        fiscal_year = self.get_financial_year()

        if not vals_list.get('challan_no'):
            seq = self.env['ir.sequence'].next_by_code('jss_code.delivery.challan') or '/'
            vals_list['challan_no'] = f"JSS/DC/{fiscal_year}/{seq}"

        if self.env.user.has_group('jss_code.group_super_user') or self.env.user.has_group('jss_code.group_engineer'):
            return super().create(vals_list)
        res = super().create(vals_list)
        return res

    def action_generate_pdf(self):
        self.ensure_one()
        self.check_user_has_permission('download')
        res = self.env.ref('jss_code.action_report_delivery_challan_pdf').report_action(self)
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
            self.message_post(body=f"Permission to download marked as used by {self.env.user.name} for record {self.challan_no}.")
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

    # def print_challan_pdf(self):
    #     return self.env.ref('jss.action_report_delivery_challan_pdf').report_action(self)


class DeliveryChallanLine(models.Model):
    _name = 'delivery.challan.line'
    _description = 'Delivery Challan Line'

    challan_id = fields.Many2one('delivery.challan', string="Delivery Challan",tracking=True)
    sn = fields.Integer(string="S/N",tracking=True)
    description = fields.Char(string="Description",tracking=True)
    part_no = fields.Char(string="Part No.",tracking=True)
    batch_no = fields.Char(string="Batch No.",tracking=True)
    lot_no = fields.Char(string="Lot No.",tracking=True)
    qty = fields.Float(string="QTY",tracking=True)
    remarks = fields.Char(string="Remarks",tracking=True)

class DeliveryContactUser(models.Model):
    _name = 'delivery.contact.user'
    _description = 'Delivery Contact User'
    _rec_name = 'user'

    user = fields.Char('User name')
