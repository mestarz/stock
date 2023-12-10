import torch
import torch.nn as nn
from torch import optim
from torch.utils.data import Dataset
from torch.utils.data import DataLoader, random_split

import numpy as np
import data
import utils


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


class StockPredictionModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_heads, num_layers):
        super(StockPredictionModel, self).__init__()

        # Multi-head self-attention layer
        self.self_attn = nn.MultiheadAttention(input_size, num_heads)

        # Position-wise feedforward layer
        self.feedforward = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size)
        )

        # Layer normalization
        self.layer_norm1 = nn.LayerNorm(hidden_size)
        self.layer_norm2 = nn.LayerNorm(hidden_size)

        # Dropout
        self.dropout = nn.Dropout(0.1)

        # Transformer encoder layers
        self.transformer_encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=hidden_size,
                nhead=num_heads,
                dim_feedforward=hidden_size,
                dropout=0.1,
                activation='relu',
                batch_first=True
            ),
            num_layers=num_layers
        )

        # Output layer
        self.output_layer = nn.Linear(hidden_size, 1)

    def forward(self, x):
        # Self-attention layer
        attn_output, _ = self.self_attn(x, x, x)

        # Residual connection and layer normalization
        x = self.layer_norm1(x + attn_output)

        # Feedforward layer
        ff_output = self.feedforward(x)

        # Residual connection and layer normalization
        x = self.layer_norm2(x + ff_output)

        # Transformer encoder layers
        x = self.transformer_encoder(x)

        # Global average pooling
        x = x.mean(dim=0)

        # Output layer
        x = self.output_layer(x)

        return x


if __name__ == '__main__':
    # 创建模型
    input_size = 64  # 输入序列长度
    output_size = 4  # 输出序列长度
    hidden_size = 256  # 隐藏层维度
    num_heads = 64  # 注意力头数
    num_layers = 256  # Transformer编码器层数

    stock_data = data.DataMacine(sample_num=1000).sample_only_price("SHSE.600000", utils.Frequency.Frequency_Day, 2023)
    dataset = StockDataset(stock_data, input_size, output_size)

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    # 创建数据加载器
    batch_size = 32
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    model = StockPredictionModel(1, hidden_size, 1, num_layers)

    # 定义损失函数和优化器
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    print(model)
    # i = 0
    # for inputs, tragets in train_loader:
    #     if len(inputs) != batch_size:
    #         continue
    #     print(i)
    #     print(inputs.shape)
    #     print(tragets.shape)
    #     i = i + 1

    # 训练模型
    num_epochs = 10
    for epoch in range(num_epochs):
        model.train()
        for inputs, targets in train_loader:
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
