python train_NetFormer_sim.py --out_folder='../output/NetFormer_sim/' --neuron_num=200 --tau=1 --weight_scale=1 --init_scale=1 --error_scale=3.5 --total_time=30000 --data_random_seed=42 --window_size=100 --predict_window_size=1 --model_type=NetFormer --spatial_partial_measurement=200 --learning_rate=1e-3 --attention_activation=none --model_random_seed=12 --scheduler=cycle --dim_E=200