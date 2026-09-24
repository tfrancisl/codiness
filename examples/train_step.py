import torch
import torch.nn.functional as F


def train_step(model, optimizer, batch):
    """Run one optimisation step and return the loss."""
    inputs, targets = batch
    optimizer.zero_grad()
    logits = model(inputs)
    loss = F.cross_entropy(logits, targets)
    loss.backward()
    optimizer.step()
    return loss.item()
