import numpy as np
import pandas as pd

df = pd.read_csv('balance_data.csv')
df= df.sample(n=50000, random_state=42).reset_index(drop=True)
theta = df['theta'].values.astype(np.float32)
theta_dot = df['theta_dot'].values.astype(np.float32)
u = df['u'].values.astype(np.float32)

u_scale = np.max(np.abs(u))
u_norm = u / u_scale

print(u_scale)

###############################################################

SEQ_LEN = 32

X = []
Y = []

for i in range(len(df) - SEQ_LEN):
    seq = np.stack([theta[i:i+SEQ_LEN], theta_dot[i:i+SEQ_LEN]], axis=1)
    X.append(seq)
    Y.append(u_norm[i + SEQ_LEN])

X = np.array(X, dtype=np.float32)
Y = np.array(Y, dtype=np.float32)

print(X.shape, Y.shape)

###############################################################

import torch
import torch.nn as nn
from ncps.torch import CfC
from ncps.wirings import AutoNCP

device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
print(f"using {device}")

X_t = torch.tensor(X).to(device)
Y_t = torch.tensor(Y).unsqueeze(1).to(device)

wiring = AutoNCP(16, 1)
model = CfC(2, wiring, batch_first=True).to(device)
#readout = nn.Linear(16, 1)

print(model)

##############################################################

optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()

dataset = torch.utils.data.TensorDataset(X_t, Y_t)
loader = torch.utils.data.DataLoader(dataset, batch_size=64, shuffle=True)

for epoch in range(200):
    total_loss = 0
    for xb, yb in loader:
        out, _ = model(xb)
        pred = out[:, -1, :]
        loss = loss_fn(pred, yb)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    if epoch % 10 == 0:
        print(f"epoch {epoch:3d}  loss={total_loss/len(loader):.6f}")

############################################################

torch.save({
    'model' : model.state_dict(),
    'u_scale' : u_scale
    }, 'cfc_balancer.pt')

print("Saved!")        

###########################################################

model.eval()

tests = [
    (0.1, 0.0),   # leaning right, still
    (-0.1, 0.0),  # leaning left, still
    (0.0, 0.5),   # upright but falling right
    (0.05, 0.3),  # leaning and falling
]

for theta_test, tdot_test in tests:
    pid_u = 120.0 * theta_test + 25.0 * tdot_test
    
    seq = np.zeros((1, 32, 2), dtype=np.float32)
    seq[0, -1, 0] = theta_test
    seq[0, -1, 1] = tdot_test
    x = torch.tensor(seq).to(device)
    
    with torch.no_grad():
        out, _ = model(x)
        cfc_u = out[0, -1, 0].item() * u_scale

    print(f"theta={theta_test:+.2f} tdot={tdot_test:+.2f}  PID={pid_u:+6.1f}  CfC={cfc_u:+6.1f}")
