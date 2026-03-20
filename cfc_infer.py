import json
import numpy as np
import pandas as pd
import torch
from ncps.torch import CfC
from ncps.wirings import AutoNCP

# load weights
with open('weights.json', 'r') as f:
    w = json.load(f)

u_scale = w['u_scale']
for key in w:
    if key != 'u_scale':
        w[key] = np.array(w[key], dtype=np.float32)

# hidden state
h0 = np.zeros(9, dtype=np.float32)
h1 = np.zeros(6, dtype=np.float32)
h2 = np.zeros(1, dtype=np.float32)

def tanh(x):    return np.tanh(x)
def sigmoid(x): return 1.0 / (1.0 + np.exp(-x))

def reset_hidden():
    global h0, h1, h2
    h0 = np.zeros(9, dtype=np.float32)
    h1 = np.zeros(6, dtype=np.float32)
    h2 = np.zeros(1, dtype=np.float32)

def cfc_step(theta, theta_dot, ts=1.0):
    global h0, h1, h2
    x0  = np.concatenate([np.array([theta, theta_dot]), h0])
    ff1 = tanh((w['rnn_cell.layer_0.ff1.weight'] * w['rnn_cell.layer_0.sparsity_mask']) @ x0 + w['rnn_cell.layer_0.ff1.bias'])
    ff2 = tanh((w['rnn_cell.layer_0.ff2.weight'] * w['rnn_cell.layer_0.sparsity_mask']) @ x0 + w['rnn_cell.layer_0.ff2.bias'])
    t   = sigmoid(w['rnn_cell.layer_0.time_a.weight'] @ x0 + w['rnn_cell.layer_0.time_a.bias'] * ts + w['rnn_cell.layer_0.time_b.weight'] @ x0 + w['rnn_cell.layer_0.time_b.bias'])
    h0  = ff1 * (1.0 - t) + t * ff2

    x1  = np.concatenate([h0, h1])
    ff1 = tanh((w['rnn_cell.layer_1.ff1.weight'] * w['rnn_cell.layer_1.sparsity_mask']) @ x1 + w['rnn_cell.layer_1.ff1.bias'])
    ff2 = tanh((w['rnn_cell.layer_1.ff2.weight'] * w['rnn_cell.layer_1.sparsity_mask']) @ x1 + w['rnn_cell.layer_1.ff2.bias'])
    t   = sigmoid(w['rnn_cell.layer_1.time_a.weight'] @ x1 + w['rnn_cell.layer_1.time_a.bias'] * ts + w['rnn_cell.layer_1.time_b.weight'] @ x1 + w['rnn_cell.layer_1.time_b.bias'])
    h1  = ff1 * (1.0 - t) + t * ff2

    x2  = np.concatenate([h1, h2])
    ff1 = tanh((w['rnn_cell.layer_2.ff1.weight'] * w['rnn_cell.layer_2.sparsity_mask']) @ x2 + w['rnn_cell.layer_2.ff1.bias'])
    ff2 = tanh((w['rnn_cell.layer_2.ff2.weight'] * w['rnn_cell.layer_2.sparsity_mask']) @ x2 + w['rnn_cell.layer_2.ff2.bias'])
    t   = sigmoid(w['rnn_cell.layer_2.time_a.weight'] @ x2 + w['rnn_cell.layer_2.time_a.bias'] * ts + w['rnn_cell.layer_2.time_b.weight'] @ x2 + w['rnn_cell.layer_2.time_b.bias'])
    h2  = ff1 * (1.0 - t) + t * ff2

    return float(h2[0]) * u_scale

# load pytorch model for comparison
checkpoint = torch.load('cfc_balancerV1.pt', weights_only=False)
pt_model = CfC(2, AutoNCP(16, 1), batch_first=True)
pt_model.load_state_dict(checkpoint['model'])
pt_model.eval()

df = pd.read_csv('balance_data.csv')

# cross-check: step through rows 33-66 and compare
reset_hidden()
hx = None
for i in range(33, 67):
    row = df.iloc[i]
    manual_u = cfc_step(row['theta'], row['theta_dot'])
    x = torch.tensor([[[row['theta'], row['theta_dot']]]], dtype=torch.float32)
    with torch.no_grad():
        out, hx = pt_model(x, hx)
    pt_u = out[0, 0, 0].item() * u_scale

print(f"manual={manual_u:.2f}  pytorch={pt_u:.2f}  true={df.iloc[66]['u']:.2f}")
