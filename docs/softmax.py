import numpy as np

def softmax(x):
    """
    用NumPy实现softmax函数
    
    Args:
        x (np.array): 包含原始分数的NumPy数组.
    
    Returns:
        np.array: 转换后的概率分布数组.
    """
    # 减去最大值以避免数值溢出问题
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

# 知识竞赛的原始分数
scores = np.array([2.0, 1.0, 0.1])

# 计算Softmax概率
probabilities = softmax(scores)

print("原始分数:", scores)
print("Softmax概率:", probabilities)
print("概率总和:", np.sum(probabilities))

# 另一个例子，分差更大
scores2 = np.array([5.0, 2.0, -1.0])
probabilities2 = softmax(scores2)

print("\n----------------------")
print("原始分数2:", scores2)
print("Softmax概率2:", probabilities2)
print("概率总和2:", np.sum(probabilities2))

# 一个更极端的例子，其中一个分数非常大
scores3 = np.array([10.0, 2.0, 1.0])
probabilities3 = softmax(scores3)

print("\n----------------------")
print("原始分数3:", scores3)
print("Softmax概率3:", probabilities3)
print("概率总和3:", np.sum(probabilities3))
