import os

import panel


def test_models_encoding():
    model_dir = os.path.join(panel.__path__[0], 'models')
    for file in os.listdir(model_dir):
        if file.endswith('.ts'):
            with open(os.path.join(model_dir, file)) as f:
                f.read()
