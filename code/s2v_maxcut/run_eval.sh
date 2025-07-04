#!/bin/bash

g_type=barabasi_albert

data_test=../../data/maxcut/gtype-$g_type-nrange-15-20-n_graph-1000-p-0.00-m-4.pkl

result_root=results/dqn-$g_type

# max belief propagation iteration
max_bp_iter=3

# embedding size
embed_dim=64

# gpu card id
dev_id=1

# max batch size for training/testing
batch_size=128

net_type=NewQNet
avg_global=0

# set reg_hidden=0 to make a linear regression
reg_hidden=32

# learning rate
learning_rate=0.0001

# init weights with rand normal(0, w_scale)
w_scale=0.01

# nstep
n_step=1

min_n=15
max_n=20

num_env=10
mem_size=50000

max_iter=50000

# folder to save the trained model
save_dir=$result_root/ntype-$net_type-embed-$embed_dim-nbp-$max_bp_iter-rh-$reg_hidden-ag-$avg_global

python2 evaluate.py \
    -n_step $n_step \
    -dev_id $dev_id \
    -data_test $data_test \
    -avg_global $avg_global \
    -min_n $min_n \
    -max_n $max_n \
    -num_env $num_env \
    -max_iter $max_iter \
    -mem_size $mem_size \
    -g_type $g_type \
    -learning_rate $learning_rate \
    -max_bp_iter $max_bp_iter \
    -net_type $net_type \
    -max_iter $max_iter \
    -save_dir $save_dir \
    -embed_dim $embed_dim \
    -batch_size $batch_size \
    -reg_hidden $reg_hidden \
    -momentum 0.9 \
    -l2 0.00 \
    -w_scale $w_scale
