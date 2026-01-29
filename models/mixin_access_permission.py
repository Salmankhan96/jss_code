from odoo import models, api
from odoo.exceptions import UserError


class AccessPermissionMixin(models.AbstractModel):
    _name = 'access.permission.mixin'

    def check_user_has_permission(self, permission_type):
        """
        Checks if the current user has the specified permission for the record.
        If permission is found and valid (not used), it marks it as used.
        Raises UserError if permission is not found.
        """
        self.ensure_one()
        # Super User or Engineer bypass all checks
        if self.env.user.has_group('jss_code.group_super_user') or self.env.user.has_group('jss_code.group_engineer'):
            return True

        Perm = self.env['access.permission.line']
        domain = [
            ('form_model', '=', self._name),
            ('form_record_id', '=', self.id),
            ('user_id', '=', self.env.user.id),
            ('permission_type', '=', permission_type),
            ('granted', '=', True),
            ('used', '=', False), # Only look for unused permissions
        ]
        permission = Perm.search(domain, limit=1)

        if not permission:
            raise UserError(f"You don't have permission to {permission_type} this record. Please request permission from an Engineer.")

        return True
