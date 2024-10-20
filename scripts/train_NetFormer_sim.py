import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import argparse
import torch
import torch.nn.functional as F
import pytorch_lightning as pl
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.callbacks.model_checkpoint import ModelCheckpoint
from pytorch_lightning.callbacks import LearningRateMonitor
from pytorch_lightning.loggers import TensorBoardLogger
from os import listdir
from torchmetrics import AUROC
from sklearn.metrics import r2_score

from NetFormer import data, models, tools


if __name__ == "__main__":
    # Parse arguments add all hyperparameters to the parser
    parser = argparse.ArgumentParser(description="Model Hyperparameters")

    parser.add_argument("--out_folder", help="the output folder")

    # Data
    parser.add_argument("--neuron_num", help="the number of neurons", type=int, default=200)
    parser.add_argument("--tau", help="tau", default=1)

    parser.add_argument("--weight_scale", default=1)
    parser.add_argument("--init_scale", default=1)
    parser.add_argument("--error_scale", default=3.5)

    parser.add_argument("--total_time", help="total time", default=30000)
    parser.add_argument("--data_random_seed", help="data random seed", default=42)

    parser.add_argument("--window_size", default=200)
    parser.add_argument("--predict_window_size", default=1)
    parser.add_argument("--batch_size", help="the batch size", type=int, default=32)

    parser.add_argument("--model_type", default="NetFormer")     # "NetFormer" or "GLM"
    parser.add_argument("--spatial_partial_measurement", default=200)   # between 0 and neuron_num

    # Model
    parser.add_argument("--model_random_seed", default=42)
    parser.add_argument("--attention_activation", default="none")    # "softmax" or "sigmoid" or "tanh" or "none"

    parser.add_argument("--learning_rate", help="learning rate", default=1e-4)
    parser.add_argument("--scheduler", default="cycle")    # "none" or "plateau" or "cycle"
    parser.add_argument("--weight_decay", default=0)

    parser.add_argument("--out_layer", default=False)
    parser.add_argument("--dim_E", default=200)

    args = parser.parse_args()

    # Set the hyperparameters
    out_folder = args.out_folder

    # Data

    neuron_num = int(args.neuron_num)
    tau = int(args.tau)

    weight_scale = float(args.weight_scale)
    init_scale = float(args.init_scale)
    error_scale = float(args.error_scale)

    total_time = int(args.total_time)
    data_random_seed = int(args.data_random_seed)

    window_size = int(args.window_size)
    predict_window_size = int(args.predict_window_size)
    batch_size = int(args.batch_size)

    model_type = args.model_type
    spatial_partial_measurement = int(args.spatial_partial_measurement)

    # Model

    model_random_seed = int(args.model_random_seed)
    attention_activation = args.attention_activation

    learning_rate = float(args.learning_rate)
    scheduler = args.scheduler
    weight_decay = float(args.weight_decay)

    out_layer = True if args.out_layer == "True" else False
    dim_E = int(args.dim_E)


    output_path = (
        out_folder
        + str(neuron_num)
        + "_"
        + str(tau)
        + "_"
        + str(weight_scale)
        + "_"
        + str(init_scale)
        + "_"
        + str(error_scale)
        + "_"
        + str(total_time)
        + "_"
        + str(data_random_seed)
        + "_"
        + str(window_size)
        + "_"
        + str(predict_window_size)
        + "_"
        + str(batch_size)
        + "_"
        + model_type
        + "_"
        + str(spatial_partial_measurement)
        + "_"
        + str(model_random_seed)
        + "_"
        + attention_activation
        + "_"
        + str(learning_rate)
        + "_"
        + scheduler
        + "_"
        + str(weight_decay)
        + "_"
        + str(out_layer)
        + "_"
        + str(dim_E)
    )

    checkpoint_path = output_path
    log_path = out_folder + "/log"

    data_result = data.generate_simulation_data(
        neuron_num=neuron_num,
        tau=tau,
        weight_scale=weight_scale,
        init_scale=init_scale,
        error_scale=error_scale,
        total_time=total_time,
        data_random_seed=data_random_seed,
        window_size=window_size,
        predict_window_size=predict_window_size,
        batch_size=batch_size,
        model_type=model_type,
        spatial_partial_measurement=spatial_partial_measurement,
    )
    trainloader, validloader, weight_matrix, cell_type_ids, cell_type_order, cell_type_count = data_result
    weight_matrix = weight_matrix.detach().numpy()

    # for spatial partial measurement
    if spatial_partial_measurement != neuron_num:
        neuron_num = spatial_partial_measurement

    single_model = models.NetFormer_sim(
        model_random_seed=model_random_seed,
        neuron_num=neuron_num,
        window_size=window_size,
        learning_rate=learning_rate,
        scheduler=scheduler,
        predict_window_size=predict_window_size,
        attention_activation=attention_activation,
        weight_decay=weight_decay,
        out_layer=out_layer,
        dim_E=dim_E,
    )

    es = EarlyStopping(monitor="VAL_loss", patience=20)
    checkpoint_callback = ModelCheckpoint(
        checkpoint_path, monitor="VAL_loss", mode="min", save_top_k=1
    )
    lr_monitor = LearningRateMonitor()
    logger = TensorBoardLogger(log_path, name="model")
    trainer = pl.Trainer(
        devices=[0],
        accelerator="gpu",
        callbacks=[es, checkpoint_callback, lr_monitor],
        benchmark=False,
        profiler="simple",
        logger=logger,
        max_epochs=1000,
    )

    trainer.fit(single_model, trainloader, validloader)


    ############################################################################################################
    # Evaluate Model Performance
    ############################################################################################################

    model_checkpoint_path = checkpoint_path + "/" + listdir(checkpoint_path)[-1]
    train_results = trainer.predict(single_model, dataloaders=[trainloader], ckpt_path=model_checkpoint_path)

    attentions = []
    for i in range(len(train_results)):
        x_hat = train_results[i][0]    # batch_size * (neuron_num*time)
        x = train_results[i][1]
        attention = train_results[i][2]
        
        attention = attention.view(-1, neuron_num, neuron_num)
        attentions.append(attention)

    attentions = torch.cat(attentions, dim=0).cpu().numpy()    # N * neuron_num * neuron_num
    avg_attention = np.mean(attentions, axis=0)   # neuron_num * neuron_num
    W = avg_attention

    # Activity prediction on validation set ###################################################################

    val_results = trainer.predict(single_model, dataloaders=[validloader], ckpt_path=model_checkpoint_path)

    predictions = []
    ground_truths = []

    for i in range(len(val_results)):
        x_hat = val_results[i][0]    # batch_size * (neuron_num*time)
        x = val_results[i][1]

        predictions.append(x_hat)
        ground_truths.append(x)

    predictions = torch.cat(predictions, dim=0).cpu().numpy()  # N * neuron_num * window_size
    ground_truths = torch.cat(ground_truths, dim=0).cpu().numpy()  # N * neuron_num * window_size
    pred_corr = stats.pearsonr(predictions.flatten(), ground_truths.flatten())[0]
    R_squared = r2_score(ground_truths.flatten(), predictions.flatten())
    MSE = np.mean((predictions.flatten() - ground_truths.flatten())**2)

    plt.scatter(predictions.flatten(), ground_truths.flatten(), s=1)
    plt.title("val_corr = " + str(pred_corr)[:7] + ", R^2 = " + str(R_squared)[:7] + ", MSE = " + str(MSE)[:7])
    plt.xlabel("Predictions")
    plt.ylabel("Ground Truths")
    plt.savefig(output_path + "/scatter_VAL.png")
    plt.close()

    for i in range(5):
        plt.subplot(5, 1, i+1)
        plt.plot(predictions[:100, i, 0], label="Prediction")
        plt.plot(ground_truths[:100, i, 0], label="Ground Truth")
    plt.legend()
    plt.savefig(output_path + "/curve.png")
    plt.close()

    # Connectivity inference evaluation ########################################################################

    corr_strength_NN = np.corrcoef(W.flatten(), weight_matrix.flatten())[0, 1]
    spearman_corr_strength_NN = stats.spearmanr(W.flatten(), weight_matrix.flatten())[0]

    strength_matrix = np.zeros((4, 4))
    strength_matrix[0, 0] = 0.11
    strength_matrix[1, 0] = 0.27
    strength_matrix[2, 0] = 0.1
    strength_matrix[3, 0] = 0.45

    strength_matrix[0, 1] = -0.44
    strength_matrix[1, 1] = -0.47
    strength_matrix[2, 1] = -0.44
    strength_matrix[3, 1] = -0.23

    strength_matrix[0, 2] = -0.16
    strength_matrix[1, 2] = -0.18
    strength_matrix[2, 2] = -0.19
    strength_matrix[3, 2] = -0.17

    strength_matrix[0, 3] = -0.06
    strength_matrix[1, 3] = -0.10
    strength_matrix[2, 3] = -0.17
    strength_matrix[3, 3] = -0.10

    cell_type_id2cell_type = {0:'EC', 1:'Pvalb', 2:'Sst', 3:'Vip'}

    KK_strength = tools.NN2KK_remove_no_connection_sim(
        connectivity_matrix_new=W,
        connectivity_matrix_GT=weight_matrix, 
        cell_type_id2cell_type=cell_type_id2cell_type,
        cell_type_count=cell_type_count
    )
    corr_strength_KK = np.corrcoef(KK_strength.flatten(), strength_matrix.flatten())[0, 1]
    spearman_corr_strength_KK = stats.spearmanr(KK_strength.flatten(), strength_matrix.flatten())[0]

    # Plot

    # KK
    max_abs = np.max(np.abs(KK_strength))
    plt.imshow(KK_strength, interpolation="nearest", cmap='RdBu_r', vmin=-max_abs, vmax=max_abs)
    plt.colorbar()
    plt.xlabel("Pre")
    plt.ylabel("Post")
    plt.title("KK_strength, corr = " + str(corr_strength_KK)[:7] + ", spearman = " + str(spearman_corr_strength_KK)[:7])
    plt.savefig(output_path + "/KK_strength.png")
    plt.close()

    np.save(output_path + "/Estimated_KK_strength.npy", KK_strength)

    # NN
    max_abs = np.max(np.abs(W))
    plt.imshow(W, cmap='RdBu_r', vmin=-max_abs, vmax=max_abs)
    plt.colorbar()
    plt.title("W" + " (corr: " + str(corr_strength_NN)[:6] + ") " + " (spearman: " + str(spearman_corr_strength_NN)[:6] + ")")
    plt.savefig(output_path + "/NN_strength.png")
    plt.close()

    np.save(output_path + "/Estimated_NN_strength.npy", W)

    # GT_KK
    max_abs = np.max(np.abs(strength_matrix))
    plt.imshow(strength_matrix, cmap='RdBu_r', vmin=-max_abs, vmax=max_abs)
    plt.colorbar()
    plt.title("GT_(cell_type_level)")
    plt.savefig(output_path + "/GT_KK_strength.png")
    plt.close()

    # GT_NN
    max_abs = np.max(np.abs(weight_matrix))
    plt.imshow(weight_matrix, cmap='RdBu_r', vmin=-max_abs, vmax=max_abs)
    plt.colorbar()
    plt.title("GT")
    plt.savefig(output_path + "/GT_NN_strength.png")
    plt.close()