import numpy as np
import pandas as pd
import random

df = pd.read_csv('balance_data_extremes.csv')

# keep episodes that have significant action, but keep ALL their rows
interesting_episodes = df.groupby('episode').apply(
    lambda ep: (abs(ep['u']) > 3).sum() > 20
)
interesting_eps = interesting_episodes[interesting_episodes].index
df = df[df['episode'].isin(interesting_eps)].reset_index(drop=True)
print(f"kept {df['episode'].nunique()} episodes, {len(df)} rows")

# balance: oversample large disturbance rows 3x
'''
df_small = df[abs(df['u']) < 10]
df_large = df[abs(df['u']) >= 10]
df = pd.concat([df_small, df_large, df_large, df_large]).reset_index(drop=True)
print(f"balanced: {len(df)} rows, large: {len(df_large)*3}")
'''

# build sequences respecting episode boundaries
SEQ_LEN = 64
X, Y = [], []  # ← initialize as empty lists first

for ep_id in df['episode'].unique():
    ep = df[df['episode'] == ep_id].reset_index(drop=True)
    theta     = ep['theta'].values.astype(np.float32)
    theta_dot = ep['theta_dot'].values.astype(np.float32)
    u         = ep['u'].values.astype(np.float32)
    for i in range(len(ep) - SEQ_LEN):
        seq = np.stack([theta[i:i+SEQ_LEN], theta_dot[i:i+SEQ_LEN]], axis=1)
        X.append(seq)
        Y.append(u[i + SEQ_LEN])

# ← convert after the loop
X = np.array(X, dtype=np.float32)
Y = np.array(Y, dtype=np.float32)
u_scale = np.max(np.abs(Y))
Y = Y / u_scale
print(X.shape, Y.shape)
# look at one episode's u values
ep0 = df[df['episode'] == 0]['u'].values
print("episode 0 u sample:", ep0[:20])
print("episode 0 u std:", ep0.std())
print("u value counts at extremes:")
print("u == 30:", (df['u'] == 30.0).sum())
print("u == -30:", (df['u'] == -30.0).sum())
print("u between -5 and 5:", ((df['u'] > -5) & (df['u'] < 5)).sum())

###############################################################

import torch
import torch.nn as nn
from ncps.torch import CfC
from ncps.wirings import AutoNCP

device = torch.device('cpu')
print(f"using {device}")

X_t = torch.tensor(X).to(device)
Y_t = torch.tensor(Y).unsqueeze(1).to(device)

wiring = AutoNCP(32, 1)
model = CfC(2, wiring, batch_first=True).to(device)
#readout = nn.Linear(16, 1)

print(model)

print("u_scale:", u_scale)
print("Y min/max after norm:", Y.min(), Y.max())
print("X min/max:", X.min(), X.max())

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
