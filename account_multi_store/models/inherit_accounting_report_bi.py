from odoo import models, fields, api

class AccountingReportBi(models.TransientModel):
    _inherit = "accounting.report.bi"

    store_ids = fields.Many2many(
        'res.store',string='Sucursal'
)

    @api.onchange('store_ids')
    def _set_jorunal_store(self):
        """
        Cargar diarios de acuerdo a la sucursal y para doble contabilidad
        """
        if self.store_ids:
            store_ids = self.store_ids + self.store_ids.mapped('child_ids')
            journal_ids = self.env['account.journal'].search([('store_id','in', store_ids.ids)])
            if journal_ids:
                self.journal_ids = [(6, 0, journal_ids.ids)]
