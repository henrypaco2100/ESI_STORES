# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AutomatedSaleStore(models.Model):
    _inherit = 'automated.sale'

    store_id = fields.Many2one(
        'res.store', string='Sucursal', required=True,
        default=lambda self: self.env.user.store_id if self.env.user.store_id else False,
    )

    @api.onchange('company_id')
    def _onchange_company_id_store_esi(self):
        for rec in self:
            if rec.store_id and rec.store_id.company_id and rec.store_id.company_id != rec.company_id:
                rec.store_id = False

    @api.onchange('store_id')
    def _onchange_store_id_esi(self):
        for rec in self:
            if rec.st_almacen and rec.st_almacen.store_id != rec.store_id:
                rec.st_almacen = False
            if rec.sales_journal and rec.sales_journal.store_id and rec.sales_journal.store_id != rec.store_id:
                rec.sales_journal = False
            if rec.payment_journal and rec.payment_journal.store_id and rec.payment_journal.store_id != rec.store_id:
                rec.payment_journal = False
            if rec.store_id and not rec.st_almacen:
                warehouses = self.env['stock.warehouse'].search([
                    ('company_id', '=', rec.company_id.id),
                    ('store_id', '=', rec.store_id.id),
                ], limit=2)
                if len(warehouses) == 1:
                    rec.st_almacen = warehouses

    @api.constrains('store_id', 'company_id', 'st_almacen', 'sales_journal', 'payment_journal')
    def _check_store_configuration_esi(self):
        for rec in self:
            if rec.store_id and rec.store_id.company_id and rec.store_id.company_id != rec.company_id:
                raise ValidationError(_('La sucursal no pertenece a la compañía seleccionada.'))
            if rec.st_almacen and rec.st_almacen.store_id != rec.store_id:
                raise ValidationError(_('El almacén no pertenece a la sucursal seleccionada.'))
            for journal in (rec.sales_journal, rec.payment_journal):
                if journal and journal.store_id and journal.store_id != rec.store_id:
                    raise ValidationError(_('El diario %s no pertenece a la sucursal seleccionada.') % journal.display_name)


class SaleOrderStore(models.Model):
    _inherit = 'sale.order'

    work_process_order_id = fields.Many2one(
        'automated.sale', string='Tipo de Venta', copy=True,
        domain=lambda self: self._esi_store_sale_type_domain(),
    )

    @api.model
    def _esi_store_sale_type_domain(self):
        domain = [('company_id', '=', self.env.user.company_id.id), ('active', '=', True)]
        user = self.env.user
        if user.store_id:
            domain.append(('store_id', 'child_of', [user.store_id.id]))
        elif user.store_ids:
            domain.append(('store_id', 'in', user.store_ids.ids))
        return domain

    @api.model
    def _esi_sale_type_vals(self, sale_type):
        vals = super()._esi_sale_type_vals(sale_type)
        vals['store_id'] = sale_type.store_id.id or False
        return vals

    @api.onchange('work_process_order_id')
    def _onchange_work_process_order_id_store_esi(self):
        res = super()._onchange_work_process_order_id_esi()
        for order in self:
            order.store_id = order.work_process_order_id.store_id if order.work_process_order_id else False
        return res

    def write(self, vals):
        vals = dict(vals)
        if 'work_process_order_id' in vals and not vals.get('work_process_order_id'):
            vals['store_id'] = False
        return super().write(vals)

    def _esi_validate_sale_type(self):
        res = super()._esi_validate_sale_type()
        for order in self:
            sale_type = order.work_process_order_id
            if not sale_type.store_id:
                raise UserError(_('El Tipo de Venta debe tener una Sucursal configurada.'))
            if sale_type.st_almacen.store_id != sale_type.store_id:
                raise UserError(_('El almacén del Tipo de Venta no corresponde a su Sucursal.'))
            for journal in (sale_type.sales_journal, sale_type.payment_journal):
                if journal.store_id and journal.store_id != sale_type.store_id:
                    raise UserError(_('Los diarios del Tipo de Venta deben corresponder a la misma sucursal.'))
        return res
