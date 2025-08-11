from behaviors import BaseBehaviour
import py_trees

BEHAVIOR_CONFIGS = {
    "Uyan": {
        "prompt": "Kalkmak için 'k', devam için 'd', idle için 'i', son için 'e': ",
        "valid_inputs": ['k', 'd', 'i', 'e'],
        "success_inputs": ['k']
    },
    "Kahvalti": {
        "prompt": "Çalışmaya gitmek için 'c', spor yapmak için 's', idle için 'i', son için 'e': ",
        "valid_inputs": ['c', 's', 'i', 'e'],
        "success_inputs": ['c', 's']
    },
    "Calis": {
        "prompt": "Dinlenmek için 'd', idle için 'i', son için 'e': ",
        "valid_inputs": ['d', 'i', 'e'],
        "success_inputs": ['d']
    },
    "Spor": {
        "prompt": "Dinlenmek için 'd', idle için 'i', son için 'e': ",
        "valid_inputs": ['d', 'i', 'e'],
        "success_inputs": ['d']
    },
    "Dinlen": {
        "prompt": "Uyumak için 'u', idle için 'i', son için 'e': ",
        "valid_inputs": ['u', 'i', 'e'],
        "success_inputs": ['u']
    }
}

def create_action_sequence(node, action_name, rest_name="Dinlen"):
    sequence = py_trees.composites.Sequence(name=f"{action_name}Akisi", memory=True)
    sequence.add_children([
        BaseBehaviour(node, action_name, **BEHAVIOR_CONFIGS[action_name]),
        BaseBehaviour(node, rest_name, **BEHAVIOR_CONFIGS[rest_name])
    ])
    return sequence

def create_behavior_tree(node):
    root = py_trees.composites.Selector(name="Root", memory=True)
    main_flow = py_trees.composites.Sequence(name="AnaAkis", memory=True)
    secim_agaci = py_trees.composites.Selector(name="SecimAgaci", memory=True)
    secim_agaci.add_children([
        create_action_sequence(node, "Calis"),
        create_action_sequence(node, "Spor")
    ])
    main_flow.add_children([
        BaseBehaviour(node, "Uyan", **BEHAVIOR_CONFIGS["Uyan"]),
        BaseBehaviour(node, "Kahvalti", **BEHAVIOR_CONFIGS["Kahvalti"]),
        secim_agaci
    ])
    from behaviors import IdleBehaviour
    root.add_children([main_flow, IdleBehaviour(node)])
    return root