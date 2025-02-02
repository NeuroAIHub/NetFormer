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
  * Nonlinear and Nonstationary System Simulation
  * Spike-Timing-Dependent Plasticity (STDP) Simulation
  * Task-trained RNN
  * Connectivity-Constrained Simulation
  * NetFormer in Networks with Spurious Correlations
    * Network with continuous activity
    * Network with spiking activity
    
* Neural Data
  * [Bugeon et al. 2022, Nature](https://www.nature.com/articles/s41586-022-04915-7) (A transcriptomic axis predicts state modulation of cortical interneurons), download dataset from this [link](https://figshare.com/articles/dataset/A_transcriptomic_axis_predicts_state_modulation_of_cortical_interneurons/19448531).

## Fit NetFormer to Data

### Nonlinear and Nonstationary System Simulation
Data generation, model fitting, and results visualization are all in `toy_systems/toy_systems.ipynb`. 

### Spike-Timing-Dependent Plasticity (STDP) Simulation
Run `STDP/run_netformer_STDP.py` for data generation and model fitting. Results visualization is in `STDP/STDP_plots.ipynb`. 

### Connectivity-Constrained Simulation

```bash
cd scripts
bash train_NetFormer_sim_connectivity_constrained.sh
```

### NetFormer in Networks with Spurious Correlations

 * Network with continuous activity

 ```bash
 cd scripts
 bash train_NetFormer_sim_ring_circuit.sh
 ```

 * Network with spiking activity
   
 Data generation is in `spurious_corr_spike_sim/data_generation.ipynb`. Run `spurious_corr_spike_sim/run_netformer_spk.py` for model fitting. Results visualization is in `spurious_corr_spike_sim/results_visualize.ipynb`. 
   
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
   

## Citations
