import os
import numpy as np
import pandas as pd
from deap import creator, base, tools, algorithms
from multiprocessing import Pool
from scipy.sparse import lil_matrix

# 数据路径
data_path_1 = 'C:/Users/18493/Desktop/mathorcup/附件2：冲突及干扰矩阵数据.xlsx'
data_path_2 = 'C:/Users/18493/Desktop/mathorcup/附件3：混淆矩阵数据.xlsx'
data_path_3 = 'D:\PycharmProjects\mathorcup_2\附件1：小区基本信息.xlsx'

# 读取数据
xiaoqu_data = pd.read_excel(data_path_3)
xiaoqu_list = xiaoqu_data['小区编号'].tolist()

conflict_data = pd.read_excel(data_path_1)  # 冲突
interference_data = pd.read_excel(data_path_1)  # 模3干扰
confusion_data = pd.read_excel(data_path_2)  # 混淆

# 使用pickle文件保存和加载数据，节省加载时间
conflict_data.to_pickle('conflict_dataframe_origin.pkl')
interference_data.to_pickle('interference_dataframe_origin.pkl')
confusion_data.to_pickle('confusion_dataframe_origin.pkl')

conflict_data = pd.read_pickle('conflict_dataframe_origin.pkl')  # 冲突
interference_data = pd.read_pickle('interference_dataframe_origin.pkl')  # 模3干扰
confusion_data = pd.read_pickle('confusion_dataframe_origin.pkl')  # 混淆

# 构建稀疏矩阵函数
def build_matrix(data, col1, col2, value_col):
    index_map = {k: i for i, k in enumerate(xiaoqu_list)}
    size = len(xiaoqu_list)
    matrix = lil_matrix((size, size), dtype=np.float32)
    for _, row in data.iterrows():
        i = index_map.get(row[col1])
        j = index_map.get(row[col2])
        if i is not None and j is not None:
            matrix[i, j] += row[value_col]
            matrix[j, i] += row[value_col]
    return matrix.tocsr()  # 转换为CSR格式以优化数值计算

# 构建冲突、干扰和混淆矩阵
conflict_matrix = build_matrix(conflict_data, '小区编号', '邻小区编号', '冲突MR数')
interference_matrix = build_matrix(interference_data, '小区编号', '邻小区编号', '干扰MR数')
confusion_matrix = build_matrix(confusion_data, '小区0编号', '小区1编号', '混淆MR数')

# 目标函数
def objective_function(pci_list, w_conflict=1, w_confusion=1, w_interference=1):
    pci_conflict = np.sum(conflict_matrix[i, j] for i in range(len(pci_list)) for j in range(i + 1, len(pci_list)) if pci_list[i] == pci_list[j])
    pci_confusion = np.sum(confusion_matrix[i, j] for i in range(len(pci_list)) for j in range(i + 1, len(pci_list)) if pci_list[i] == pci_list[j])
    pci_interference = np.sum(interference_matrix[i, j] for i in range(len(pci_list)) for j in range(i + 1, len(pci_list)) if pci_list[i] % 3 == pci_list[j] % 3)
    return (w_conflict * pci_conflict) + (w_confusion * pci_confusion) + (w_interference * pci_interference)

# 评估函数
def evaluate_individual(ind):
    return (objective_function(ind),)

# 初始化遗传算法工具箱
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)
toolbox = base.Toolbox()
toolbox.register("attr_pci", np.random.randint, 0, 1008)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_pci, len(xiaoqu_list))
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate_individual)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutUniformInt, low=0, up=1007, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

# 检查并创建结果文件夹
results_directory = 'D:/PycharmProjects/mathorcup_2/results_5'
if not os.path.exists(results_directory):
    os.makedirs(results_directory)

# Excel文件的完整路径
excel_path = os.path.join(results_directory, 'best_individual.xlsx')

# 主程序
if __name__ == '__main__':
    pool = Pool()
    toolbox.register("map", pool.map)

    # 生成种群
    population = toolbox.population(n=300)
    ngen = 100  # 世代数

    # 执行遗传算法
    result = algorithms.eaSimple(population, toolbox, cxpb=0.5, mutpb=0.2, ngen=ngen, verbose=True)

    # 输出最佳解
    best_ind = tools.selBest(population, 1)[0]
    print("Best Individual:", best_ind)
    print("Best Fitness:", best_ind.fitness.values)

    # 将最佳解保存到Excel
    best_ind_data = pd.DataFrame({
        'PCI': best_ind
    })
    best_ind_data.to_excel(excel_path, index=False)
    print(f"最佳个体已保存到 {excel_path}")

    pool.close()
    pool.join()
