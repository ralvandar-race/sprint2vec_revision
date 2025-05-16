<vscode_codeblock_uri>file:///d%3A/REVA/Capstone1/sprint2vec_revision/sprint2vec/Models/__init__.py</vscode_codeblock_uri>"""
Sprint2Vec: A Deep Learning Model for Sprint Performance Prediction
"""
from .Models.Sprint2Vec import Sprint2Vec
from .config import ExperimentConfig

__version__ = '0.1.0'
__all__ = ['Sprint2Vec', 'ExperimentConfig']
```

```python
<vscode_codeblock_uri>file:///d%3A/REVA/Capstone1/sprint2vec_revision/sprint2vec/Models/Sprint2Vec.py</vscode_codeblock_uri>import torch
import torch.nn as nn
from ..config import ExperimentConfig

class Sprint2Vec(nn.Module):
    # ...existing code...
