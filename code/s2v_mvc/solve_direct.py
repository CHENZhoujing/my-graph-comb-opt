# -*- coding: utf-8 -*-

import numpy as np
import networkx as nx
import cPickle as cp
import random
import ctypes
import os
import sys
import time
from tqdm import tqdm

sys.path.append( '%s/mvc_lib' % os.path.dirname(os.path.realpath(__file__)) )
from mvc_lib import MvcLib

def find_model_file(opt):
    max_n = int(opt['max_n'])
    min_n = int(opt['min_n'])
    log_file = '%s/log-%d-%d.txt' % (opt['save_dir'], min_n, max_n)

    best_r = 1000000
    best_it = -1
    with open(log_file, 'r') as f:
        for line in f:
            if 'average' in line:
                line = line.split(' ')
                it = int(line[1].strip())
                r = float(line[-1].strip())
                if r < best_r:
                    best_r = r
                    best_it = it
    assert best_it >= 0
    print('using iter=', best_it, 'with r=', best_r)
    return '%s/nrange_%d_%d_iter_%d.model' % (opt['save_dir'], min_n, max_n, best_it)

if __name__ == '__main__':
    api = MvcLib(sys.argv)
    
    opt = {}
    for i in range(1, len(sys.argv), 2):
        opt[sys.argv[i][1:]] = sys.argv[i + 1]

    model_file = find_model_file(opt)
    assert model_file is not None
    print('loading', model_file)
    sys.stdout.flush()
    api.LoadModel(model_file)

    import json
    
    json_file = '../../cplex/mvc/sample_graphs_n300_graph_n300.json'
    with open(json_file, 'r') as f:
        graphs_data = json.load(f)

    result_file = '%s/test-custom-graphs.csv' % (opt['save_dir'])
    # 获取当前时间作为时间戳使用，格式为YYYYMMDD_HHMMSS
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    # 从JSON文件名提取数据集信息
    dataset_name = os.path.basename(json_file).replace('.json', '')
    # 生成新的报告文件名，格式为mvc_数据集名称_时间戳
    report_file = '../../cplex/mvc/mvc_%s_%s.log' % (dataset_name, timestamp)
    
    # 获取当前时间
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    
    with open(report_file, 'w') as f_report:
        f_report.write('Minimum Vertex Cover Analysis Report\n')
        f_report.write('Generated at: %s\n' % current_time)
        f_report.write('='*80 + '\n\n')
    
    with open(result_file, 'w') as f_out:
        print('testing multiple graphs from JSON')
        sys.stdout.flush()
        
        # 初始化统计数据
        total_graphs = len(graphs_data)
        successful_solutions = 0
        total_cover_size = 0.0
        total_solve_time = 0.0
        
        for idx, graph_data in enumerate(graphs_data):
            print('\nProcessing graph %d' % (idx + 1))
            
            # 解析edges字符串为元组列表
            edges_str = graph_data['edges']
            edges = eval(edges_str)  # 将字符串转换为Python对象
            
            # 创建新图并添加边
            g = nx.Graph()
            g.add_edges_from(edges)
            
            # 处理当前图
            api.InsertGraph(g, is_test=True)
            t1 = time.time()
            val, sol = api.GetSol(idx, nx.number_of_nodes(g))
            t2 = time.time()
            solve_time = t2 - t1
            
            # 更新统计数据
            successful_solutions += 1
            total_cover_size += val
            total_solve_time += solve_time
            
            print('Graph %d solution size:' % (idx + 1), val)
            print('Graph %d vertices in solution:' % (idx + 1), [sol[i + 1] for i in range(sol[0])])
            print('Time taken:', solve_time)
            
            # 写入详细报告
            with open(report_file, 'a') as f_report:
                f_report.write('\nGraph #%d\n' % (idx + 1))
                f_report.write('-'*40 + '\n')
                f_report.write('Number of nodes: %d\n' % nx.number_of_nodes(g))
                f_report.write('Number of edges: %d\n\n' % nx.number_of_edges(g))
                f_report.write('Solution Status: Successful\n')
                f_report.write('Minimum vertex cover size: %.1f\n' % val)
                f_report.write('Selected vertices: %s\n' % str([sol[i + 1] for i in range(sol[0])]))
                f_report.write('Solve time: %.4f seconds\n\n' % solve_time)
                f_report.write('='*80 + '\n')
        
        # 计算平均值
        avg_cover_size = total_cover_size / successful_solutions if successful_solutions > 0 else 0
        avg_solve_time = total_solve_time / successful_solutions if successful_solutions > 0 else 0
        
        # 添加总结统计部分
        with open(report_file, 'a') as f_report:
            f_report.write('\n\nSummary Statistics\n')
            f_report.write('-'*40 + '\n')
            f_report.write('File processed: %s\n' % os.path.basename(json_file))
            f_report.write('Total graphs processed: %d\n' % total_graphs)
            f_report.write('Successful solutions: %d\n' % successful_solutions)
            f_report.write('Average minimum vertex cover size: %.2f\n' % avg_cover_size)
            f_report.write('Average solve time: %.4f seconds\n' % avg_solve_time)
            f_report.write('='*80 + '\n')