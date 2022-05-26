import os

import panel


def test_models_encoding():
    model_dir = os.path.join(panel.__path__[0], 'models')
    for file in os.listdir(model_dir):
        if file.endswith('.ts'):
            open(os.path.join(model_dir, file), 'r').read()
