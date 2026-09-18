# -*- coding: utf-8 -*-


def migrate(cr, version):
    """ESI correccion: retire BI-specific views from the core addon.

    The BI integration was moved to esi_account_multi_store_bi_financial so
    esi_account_multi_store no longer requires esi_bi_financial_pdf_reports.
    Removing the legacy inherited views prevents stale views from referencing
    store_ids while the optional integration addon is not installed yet.
    """
    if not version:
        return

    xmlids = (
        'sd_inherit_accounting_report_bi',
        'sd_inherit_accounting_report_bi_profit_loss',
        'sd_inherit_accounting_report_bi_general_ledger',
    )
    cr.execute(
        """
        SELECT res_id
          FROM ir_model_data
         WHERE module = 'esi_account_multi_store'
           AND model = 'ir.ui.view'
           AND name IN %s
        """,
        (xmlids,),
    )
    view_ids = [row[0] for row in cr.fetchall()]
    if view_ids:
        cr.execute('DELETE FROM ir_ui_view WHERE id IN %s', (tuple(view_ids),))

    cr.execute(
        """
        DELETE FROM ir_model_data
         WHERE module = 'esi_account_multi_store'
           AND model = 'ir.ui.view'
           AND name IN %s
        """,
        (xmlids,),
    )
