{
    "name": "MRP Employee Queue",
    "version": "18.0.1.0.0",
    "summary": "Cola de órdenes de trabajo por empleado",
    "category": "Manufacturing/Manufacturing",
    "author": "Batiplane + OCA style",
    "license": "LGPL-3",
    "depends": ["mrp", "hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_workorder_views.xml",
        "views/hr_employee_views.xml",
    ],
    "application": False,
    "installable": True,
}