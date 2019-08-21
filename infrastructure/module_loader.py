def load_all(module_name):
    import os

    dircts = []
    path = os.getcwd()
    for root, dirs, files in os.walk(path):
        for file in files:
            script = '{}.py'.format(module_name)
            if file.endswith(script):
                filepath = os.path.join(root, file)
                if 'venv' not in filepath:
                    dir_address = str(os.path.dirname(filepath))
                    dirname = dir_address.split('/')[-1]
                    dircts.append(dirname)
    print(dircts)

    for m in dircts:
        __import__('{}.{}'.format(m, module_name),
                   fromlist=['*'])

