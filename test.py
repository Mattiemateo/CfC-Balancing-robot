import torch
import numpy as np
import pandas as pd
from ncps.torch import CfC
from ncps.wirings import AutoNCP

checkpoint = torch.load('cfc_balancer.pt', weights_only=False)
u_scale = checkpoint['u_scale']

wiring = AutoNCP(16, 1)
model = CfC(2, wiring, batch_first=True)
model.load_state_dict(checkpoint['model'])
model.eval()

import numpy as np
import pandas as pd

df = pd.read_csv('balance_data.csv')
theta     = df['theta'].values.astype(np.float32)
theta_dot = df['theta_dot'].values.astype(np.float32)
u         = df['u'].values.astype(np.float32)

SEQ_LEN = 32
X, Y = [], []
for i in range(len(df) - SEQ_LEN):
    seq = np.stack([theta[i:i+SEQ_LEN], theta_dot[i:i+SEQ_LEN]], axis=1)
    X.append(seq)
    Y.append(u[i + SEQ_LEN] / u_scale)

import torch
X_t = torch.tensor(np.array(X, dtype=np.float32))
Y_t = torch.tensor(np.array(Y, dtype=np.float32)).unsqueeze(1)

for idx in [100, 500, 2000, 5000]:
    x = X_t[idx].unsqueeze(0)
    true_u = Y_t[idx].item() * u_scale

    with torch.no_grad():
        out, _ = model(x)
        cfc_u = out[0, -1, 0].item() * u_scale

    print(f"idx={idx}  true u={true_u:+.2f}  CfC={cfc_u:+.2f}")
