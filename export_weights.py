import torch
import json

checkpoint = torch.load('cfc_balancerV1.pt', weights_only=False)
state = checkpoint['model']

weights = {}
for key, tensor in state.items():
    weights[key] = tensor.cpu().numpy().tolist()

weights['u_scale'] = float(checkpoint['u_scale'])

with open('weights.json', 'w') as f:
    json.dump(weights, f, indent=2)

print("saved weights.json")
print("keys:", list(weights.keys()))
