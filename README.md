# NetFormer

## Set up environment

```bash
conda env create --name NetFormer --file environment.yml
```

Install NetFormer package in root directory

```bash
conda activate NetFormer
pip install -e .
```

## Datasets

* Simulation Data
  * Nonlinear and Nonstationary Systems Simulation
  * Spike-Timing-Dependent Plasticity (STDP) Simulation
  * Task-driven Population Activity Simulation
  * Connectivity-Constrained Simulation
  * Supplementary: Networks with Spurious Correlations
    * Network with continuous activity
    * Network with spiking activity
    
* Neural Data
  * [Bugeon et al. 2022, Nature](https://www.nature.com/articles/s41586-022-04915-7) (A transcriptomic axis predicts state modulation of cortical interneurons), download dataset from this [link](https://figshare.com/articles/dataset/A_transcriptomic_axis_predicts_state_modulation_of_cortical_interneurons/19448531).

## Fit NetFormer to Data

### Nonlinear and Nonstationary Systems Simulation
Data generation, model fitting, and results visualization are all in `toy_systems/toy_systems.ipynb`. 

### Spike-Timing-Dependent Plasticity (STDP) Simulation
For data generation and NetFormer model fitting, run `STDP/run_netformer_STDP.py` with 

`python run_netformer_STDP.py --totalsteps 100000 --npre 100 --rate 50 --histlen 5 --standardize 1 --embdim 101 --projdim 0 --maxepoch 20 --batchsize 64 --lr 0.005 --smoothlen 10000 --lrschr 0 --seeds 0 1 2 3 4`

Visualization of NetFormer results is in `STDP/STDP_plots.ipynb` (result files were not uploaded due to file size limit).


### Task-driven Population Activity Simulation
RNN models are trained on three NeuroGym tasks (example code for training RNNs is in `taskRNN/example_data_gen.ipynb`). Task-trained RNN models and activity are in `taskRNN_data/`. Run `taskRNN/run_netformer_taskrnn.py` for fitting NetFormer:
- For PerceptualDecisionMaking task: `python run_netformer_taskrnn.py --rnndim 4 --useinp 1 --histlen 5 --LN 1 --embdim 0 --projdim 0 --ptrain 0.8 --padstart 0 --maxepoch 100 --batchsize 64 --lr 0.0025 --lrschr 0 --datapath 'taskRNN_data/PerceptualDecisionMaking/' --outdir 'taskRNN_results/PerceptualDecisionMaking_results/' --seeds 0 1 2 3 4`
- For GoNogo task: `python run_netformer_taskrnn.py --rnndim 8 --useinp 1 --histlen 1 --LN 0 --embdim 0 --projdim 0 --ptrain 0.8 --padstart 0 --maxepoch 50 --batchsize 64 --lr 0.01 --lrschr 0 --datapath 'taskRNN_data/GoNogo/' --outdir 'taskRNN_results/GoNogo_results/' --seeds 0 1 2 3 4`
- For DelayComparison task: `python run_netformer_taskrnn.py --rnndim 12 --useinp 1 --histlen 5 --LN 1 --embdim 0 --projdim 0 --ptrain 0.8 --padstart 0 --maxepoch 50 --batchsize 64 --lr 0.005 --lrschr 0 --datapath 'taskRNN_data/DelayComparison/' --outdir 'taskRNN_results/DelayComparison_results/' --seeds 0 1 2 3 4`

Visualization of NetFormer results is in `taskRNN/taskrnn_netformer_{task}.ipynb` (result files were not uploaded due to file size limit).

### Connectivity-Constrained Simulation

```bash
cd scripts
bash train_NetFormer_sim_connectivity_constrained.sh
```
   
### Neural Data

* Create a data folder `data` under home directory.
* Download the dataset (Bugeon et al. 2022, Nature) to `data/Mouse/`

```bash
cd scripts
bash train_NetFormer_mouse.sh
```


## Baselines

### Nonstationary Baselines

 * LtrRNN: Clone and install [LtrRNN package](https://github.com/arthur-pe/LtrRNN). Run `notebook/nonstationary_baselines/LtrRNN.ipynb` for model fitting and evaluation on neural data.
 * AR-HMM: Clone and install [ssm package](https://github.com/lindermanlab/ssm). Run `notebook/nonstationary_baselines/arHMM.ipynb` for model fitting and evaluation on neural data.
   
### Supplementary: Networks with Spurious Correlations

 * Network with continuous activity

 ```bash
 cd scripts
 bash train_NetFormer_sim_ring_circuit.sh
 ```

 * Network with spiking activity
   
 Data generation is in `spurious_corr_spike_sim/data_generation.ipynb`. Run `spurious_corr_spike_sim/run_netformer_spk_poisson.py` for fitting NetFormer. 
 
 For recurrent strength r=0.0025, 0.005, 0.0075, 0.01, 0.0125, 0.015, 0.0175, 0.02, 0.0225, 0.025:
 - `python run_netformer_spk_poisson.py --r 0.0025  --embdim 100  --lr 0.001`
 - `python run_netformer_spk_poisson.py --r 0.005 --embdim 100 --lr 0.001`
 - `python run_netformer_spk_poisson.py --r 0.0075 --embdim 100 --lr 0.002`
 - `python run_netformer_spk_poisson.py --r 0.01 --embdim 100 --lr 0.002`
 - `python run_netformer_spk_poisson.py --r 0.0125 --embdim 100 --lr 0.002`
 - `python run_netformer_spk_poisson.py --r 0.015 --embdim 100 --lr 0.002`
 - `python run_netformer_spk_poisson.py --r 0.0175 --embdim 100 --lr 0.002`
 - `python run_netformer_spk_poisson.py --r 0.02 --embdim 100 --lr 0.002`
 - `python run_netformer_spk_poisson.py --r 0.0225 --embdim 40 --lr 0.0005`
 - `python run_netformer_spk_poisson.py --r 0.025 --embdim 100 --lr 0.002`
 - These arguments are the same for all r: `--totalsteps 100000 --skipsteps 10000 --useinp 0 --histlen 1 --LN 0 --projdim 0 --ptrain 0.8 --maxepoch 100 --batchsize 32 --lrschr 0 --usegpu 1 --datapath './' --outdir 'results/' --seeds 0 1 2`

 Visualization of NetFormer results is in `spurious_corr_spike_sim/results_visualize.ipynb` (result files were not uploaded due to file size limit). 

## Citations
```bibtex
@inproceedings{lu2025netformer,
    title     = {NetFormer: An Interpretable Model for Recovering Dynamical Connectivity in Neuronal Population Dynamics},
    author    = {Ziyu Lu and Wuwei Zhang and Trung Le and Hao Wang and Uygar Sumbul and Eric Shea-Brown and Lu Mi},
    booktitle = {Proceedings of the International Conference on Learning Representations (ICLR)},
    year      = {2025}
}
```
