import torch

# 检查是否有可用的 GPU
if torch.cuda.is_available():
    # 打印 GPU 设备数量
    print(f"Number of available GPUs: {torch.cuda.device_count()}")

    # 打印当前正在使用的 GPU 设备
    print(f"Current GPU Device: {torch.cuda.get_device_name(0)}")
else:
    print("No GPU available, using CPU.")