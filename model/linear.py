import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset
from torch.utils.data import DataLoader, random_split
import utils
import data as dm


class StockDataset(Dataset):
    def __init__(self, data, sequence_length=90, prediction_length=10):
        self.data = torch.tensor(data, dtype=torch.float32)
        self.sequence_length = sequence_length
        self.prediction_length = prediction_length

    def __len__(self):
        return len(self.data) - self.sequence_length - self.prediction_length + 1

    def __getitem__(self, idx):
        idx_end = idx + self.sequence_length + self.prediction_length
        input_data = self.data[idx:idx + self.sequence_length]
        target_data = self.data[idx + self.sequence_length:idx_end]
        return input_data, target_data


# linear
class LinearModel(nn.Module):
    def __init__(self, input_size, output_size, hidden_size=128, num_layers=2):
        super(LinearModel, self).__init__()
        self.linear = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.layers = nn.ModuleList()
        for i in range(num_layers):
            self.layers.append(nn.Linear(hidden_size, hidden_size))
            self.layers.append(nn.ReLU())
        self.output_layer = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.linear(x)
        x = self.relu(x)
        for layer in self.layers:
            x = layer(x)
        x = self.output_layer(x)
        return x


if __name__ == '__main__':
    # 创建模型
    input_size = 64  # 输入序列长度
    output_size = 4  # 输出序列长度
    hidden_size = 256  # 隐藏层维度
    num_layers = 3  # 隐藏层数

    model = LinearModel(input_size, output_size, hidden_size, num_layers)
    stock_data = dm.DataMacine(sample_num=1000).sample_only_price("SHSE.600000", utils.Frequency.Frequency_Day, 2023)
    dataset = StockDataset(stock_data, input_size, output_size)

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    # 创建数据加载器
    batch_size = 32
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    # 定义损失函数和优化器
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # 训练模型
    num_epochs = 10
    for epoch in range(num_epochs):
        model.train()
        for inputs, targets in train_loader:
            print(inputs.shape)
            if len(inputs) != batch_size:
                continue
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

        # 在验证集上评估模型性能
        model.eval()
        with torch.no_grad():
            val_loss = 0.0
            for inputs, targets in val_loader:
                outputs = model(inputs)
                val_loss += criterion(outputs, targets).item()

        val_loss /= len(val_loader)
        print(f'Epoch {epoch + 1}/{num_epochs}, Loss: {val_loss}')

    # 训练完成后，你可以保存模型的参数
    torch.save(model.state_dict(), 'stock_prediction_model.pth')
