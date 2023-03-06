predefined_roles = [
    {
        "role": "admin",
        "privileges": [
            {
                "resource": {"db": "app", "collection": "OrderProduct"},
                "actions": ["find", "insert", "remove", "update"],
            },
            {
                "resource": {"db": "app", "collection": "Category"},
                "actions": ["find", "insert", "remove", "update"],
            },
            {
                "resource": {"db": "app", "collection": "Order"},
                "actions": ["find", "insert", "remove", "update"],
            },
            {
                "resource": {"db": "app", "collection": "Product"},
                "actions": ["find", "insert", "remove", "update"],
            },
            {
                "resource": {"db": "app", "collection": "User"},
                "actions": ["find", "insert", "remove", "update"],
            },
        ],
        "roles": [],
    },
    {
        "role": "manager",
        "privileges": [
            {
                "resource": {"db": "app", "collection": "OrderProduct"},
                "actions": ["find"],
            },
            {
                "resource": {"db": "app", "collection": "Category"},
                "actions": ["find", "insert", "remove", "update"],
            },
            {
                "resource": {"db": "app", "collection": "Order"},
                "actions": [
                    "find",
                ],
            },
            {
                "resource": {"db": "app", "collection": "Product"},
                "actions": ["find", "insert", "remove", "update"],
            },
            {
                "resource": {"db": "app", "collection": "User"},
                "actions": ["find", "insert", "update"],
            },
        ],
        "roles": [],
    },
    {
        "role": "customer",
        "privileges": [
            {
                "resource": {"db": "app", "collection": "OrderProduct"},
                "actions": ["find", "insert", "remove", "update"],
            },
            {
                "resource": {"db": "app", "collection": "Category"},
                "actions": ["find"],
            },
            {
                "resource": {"db": "app", "collection": "Order"},
                "actions": ["find", "insert", "remove", "update"],
            },
            {
                "resource": {"db": "app", "collection": "Product"},
                "actions": ["find"],
            },
            {
                "resource": {"db": "app", "collection": "User"},
                "actions": ["find", "insert", "update"],
            },
        ],
        "roles": [],
    },
    {
        "role": "guest",
        "privileges": [
            {
                "resource": {"db": "app", "collection": "OrderProduct"},
                "actions": ["find"],
            },
            {
                "resource": {"db": "app", "collection": "Category"},
                "actions": ["find"],
            },
            {
                "resource": {"db": "app", "collection": "Order"},
                "actions": ["find"],
            },
            {
                "resource": {"db": "app", "collection": "Product"},
                "actions": ["find"],
            },
            {
                "resource": {"db": "app", "collection": "User"},
                "actions": ["find", "insert", "update"],
            },
        ],
        "roles": [],
    },
]
