import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ucimlrepo import fetch_ucirepo

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

import torch
from torch import nn
from torch.utils.data import TensorDataset, DataLoader
from torch.optim import Optimizer

RANDOM_STATE = 42
BATCH_SIZE = 512
EPOCHS = 10
LR = 0.01
MOMENTUM = 0.9

torch.manual_seed(RANDOM_STATE)
np.random.seed(RANDOM_STATE)

dataset = fetch_ucirepo(id=967)

X = dataset.data.features.copy()
y = dataset.data.targets.copy()

print("Исходный размер X:", X.shape)
print("Исходный размер y:", y.shape)

y = y.iloc[:, 0].astype(int)
X = X.select_dtypes(include=[np.number]).copy()

print("Размер X после выбора числовых признаков:", X.shape)
data = X.copy()
data["target"] = y.values
data = data.dropna()

X = data.drop(columns=["target"])
y = data["target"].astype(int)

print("Размер после удаления пропусков:", X.shape)
print("Количество классов:")
print(y.value_counts())

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=RANDOM_STATE,
    stratify=y
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train.values, dtype=torch.float32).view(-1, 1)
y_test_tensor = torch.tensor(y_test.values, dtype=torch.float32).view(-1, 1)

train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
test_dataset = TensorDataset(X_test_tensor, y_test_tensor)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)

class PhishingNet(nn.Module):
    def __init__(self, input_size):
        super().__init__()

        self.net = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        return self.net(x)

class PolyakSGD(Optimizer):
    def __init__(self, params, lr=0.01, beta=0.9):
        defaults = dict(lr=lr, beta=beta)
        super().__init__(params, defaults)

    @torch.no_grad()
    def step(self, closure=None):
        loss = None

        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            lr = group["lr"]
            beta = group["beta"]

            for p in group["params"]:
                if p.grad is None:
                    continue

                state = self.state[p]

                if "prev_param" not in state:
                    state["prev_param"] = p.detach().clone()

                prev_param = state["prev_param"]
                current_param = p.detach().clone()

                p.add_(p.grad, alpha=-lr)
                p.add_(current_param - prev_param, alpha=beta)

                state["prev_param"] = current_param

        return loss


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()

    total_loss = 0.0

    for X_batch, y_batch in loader:
        X_batch = X_batch.to(device)
        y_batch = y_batch.to(device)

        optimizer.zero_grad()

        logits = model(X_batch)
        loss = criterion(logits, y_batch)

        loss.backward()
        optimizer.step()

        total_loss += loss.item() * X_batch.size(0)

    return total_loss / len(loader.dataset)


def evaluate(model, loader, criterion, device):
    model.eval()

    total_loss = 0.0
    all_preds = []
    all_true = []

    with torch.no_grad():
        for X_batch, y_batch in loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)

            logits = model(X_batch)
            loss = criterion(logits, y_batch)

            probs = torch.sigmoid(logits)
            preds = (probs >= 0.5).int()

            total_loss += loss.item() * X_batch.size(0)

            all_preds.extend(preds.cpu().numpy().ravel())
            all_true.extend(y_batch.cpu().numpy().ravel())

    avg_loss = total_loss / len(loader.dataset)

    accuracy = accuracy_score(all_true, all_preds)
    precision = precision_score(all_true, all_preds, zero_division=0)
    recall = recall_score(all_true, all_preds, zero_division=0)
    f1 = f1_score(all_true, all_preds, zero_division=0)

    return avg_loss, accuracy, precision, recall, f1


def run_experiment(optimizer_name, optimizer_class, optimizer_kwargs):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = PhishingNet(input_size=X_train.shape[1]).to(device)
    model.load_state_dict(initial_weights)

    criterion = nn.BCEWithLogitsLoss()
    optimizer = optimizer_class(model.parameters(), **optimizer_kwargs)

    history = {
        "train_loss": [],
        "test_loss": [],
        "test_accuracy": [],
        "test_precision": [],
        "test_recall": [],
        "test_f1": []
    }

    for epoch in range(EPOCHS):
        train_loss = train_one_epoch(
            model,
            train_loader,
            criterion,
            optimizer,
            device
        )

        test_loss, accuracy, precision, recall, f1 = evaluate(
            model,
            test_loader,
            criterion,
            device
        )

        history["train_loss"].append(train_loss)
        history["test_loss"].append(test_loss)
        history["test_accuracy"].append(accuracy)
        history["test_precision"].append(precision)
        history["test_recall"].append(recall)
        history["test_f1"].append(f1)

        print(
            f"{optimizer_name} | "
            f"epoch {epoch + 1}/{EPOCHS} | "
            f"train_loss={train_loss:.4f} | "
            f"test_loss={test_loss:.4f} | "
            f"accuracy={accuracy:.4f} | "
            f"f1={f1:.4f}"
        )

    return model, history

base_model = PhishingNet(input_size=X_train.shape[1])
initial_weights = copy.deepcopy(base_model.state_dict())

print("\n      Библиотечный оптимизатор PyTorch SGD с momentum      ")

model_torch, history_torch = run_experiment(
    optimizer_name="PyTorch SGD momentum",
    optimizer_class=torch.optim.SGD,
    optimizer_kwargs={
        "lr": LR,
        "momentum": MOMENTUM
    }
)

print("\n      Собственный оптимизатор PolyakSGD      ")

model_polyak, history_polyak = run_experiment(
    optimizer_name="Custom PolyakSGD",
    optimizer_class=PolyakSGD,
    optimizer_kwargs={
        "lr": LR,
        "beta": MOMENTUM
    }
)


results = pd.DataFrame({
    "optimizer": ["PyTorch SGD momentum", "Custom PolyakSGD"],
    "test_loss": [
        history_torch["test_loss"][-1],
        history_polyak["test_loss"][-1]
    ],
    "accuracy": [
        history_torch["test_accuracy"][-1],
        history_polyak["test_accuracy"][-1]
    ],
    "precision": [
        history_torch["test_precision"][-1],
        history_polyak["test_precision"][-1]
    ],
    "recall": [
        history_torch["test_recall"][-1],
        history_polyak["test_recall"][-1]
    ],
    "f1": [
        history_torch["test_f1"][-1],
        history_polyak["test_f1"][-1]
    ]
})

print("\nИтоговое сравнение:")
print(results)

epochs = range(1, EPOCHS + 1)

plt.figure(figsize=(8, 5))
plt.plot(
    epochs,
    history_torch["test_accuracy"],
    marker="o",
    label="PyTorch SGD momentum"
)
plt.plot(
    epochs,
    history_polyak["test_accuracy"],
    marker="s",
    label="Custom PolyakSGD"
)

plt.xlabel("Эпоха")
plt.ylabel("Accuracy на тестовой выборке")
plt.title("Сравнение оптимизаторов")
plt.grid(True)
plt.legend()
plt.savefig("task3_accuracy_comparison.png", dpi=300, bbox_inches="tight")
plt.show()

plt.figure(figsize=(8, 5))
plt.plot(
    epochs,
    history_polyak["test_loss"],
    marker="s",
    label="Custom PolyakSGD"
)
plt.plot(
    epochs,
    history_torch["test_loss"],
    marker="o",
    label="PyTorch SGD momentum"
)


plt.xlabel("Эпоха")
plt.ylabel("Loss на тестовой выборке")
plt.title("Сравнение функции потерь")
plt.grid(True)
plt.legend()
plt.savefig("task3_loss_comparison.png", dpi=300, bbox_inches="tight")
plt.show()