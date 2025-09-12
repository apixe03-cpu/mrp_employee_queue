from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    employee_id = fields.Many2one(
        "hr.employee", string="Empleado asignado", index=True, tracking=True
    )
    employee_sequence = fields.Integer(
        string="Secuencia (empleado)", default=10, index=True
    )
    in_employee_queue = fields.Boolean(
        string="En cola del empleado",
        help="Si no está marcado, la orden no se considera en la cola personal.",
        default=True,
    )

    _order = "state desc, employee_id, employee_sequence, priority desc, id"

    def action_open(self):
        """Abre la workorder actual (helper para botones)."""
        self.ensure_one()
        action = self.env.ref("mrp.mrp_workorder_todo").read()[0]
        action.update({"res_id": self.id, "views": [(False, "form")]})
        return action

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _domain_next_wo(self):
        return [
            ("state", "in", ["ready", "progress", "waiting"]),
            ("in_employee_queue", "=", True),
            ("employee_id", "=", self.id),
        ]

    next_workorder_id = fields.Many2one(
        "mrp.workorder",
        string="Próxima orden",
        compute="_compute_next_workorder",
        store=False,
    )
    wo_queue_count = fields.Integer(
        string="Órdenes en cola", compute="_compute_wo_queue_count", store=False
    )

    def _compute_next_workorder(self):
        for emp in self:
            wo = self.env["mrp.workorder"].search(
                emp._domain_next_wo(),
                order="employee_sequence asc, priority desc, id asc",
                limit=1,
            )
            emp.next_workorder_id = wo or False

    def _compute_wo_queue_count(self):
        for emp in self:
            emp.wo_queue_count = self.env["mrp.workorder"].search_count(
                emp._domain_next_wo()
            )

    def action_employee_next_workorder(self):
        """Abre la siguiente WO asignada al empleado (la 'toma')."""
        self.ensure_one()
        wo = self.env["mrp.workorder"].search(
            self._domain_next_wo(),
            order="employee_sequence asc, priority desc, id asc",
            limit=1,
        )
        if not wo:
            raise UserError(_("No hay órdenes en la cola de %s.") % (self.name,))
        # Aquí más adelante podemos:
        # - arrancar la WO si está 'ready' (wo.button_start())
        # - imprimir ticket (report_to_printer)
        # - registrar usuario/empleado como actor
        return wo.action_open()
