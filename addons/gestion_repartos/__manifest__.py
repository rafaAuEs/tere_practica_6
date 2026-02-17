# -*- coding: utf-8 -*-
{
    'name': "Gestión de Repartos",
    'summary': "Gestión de flota, empleados y envíos para empresa de logística.",
    'description': """
        Módulo para proyecto final de 2DAM:
        - Gestión de Empleados (con foto y carnets).
        - Gestión de Vehículos (Bicicleta/Furgoneta).
        - Gestión de Clientes.
        - Gestión de Pedidos/Repartos con validaciones.
    """,
    'author': "Tu Nombre",
    'website': "http://www.tuweb.com",
    'category': 'Logistics',
    'version': '1.0',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'application': True,
    'installable': True,
}