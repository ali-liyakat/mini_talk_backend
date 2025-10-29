# algorithms/fedavg.py
import numpy as np

def aggregate(weights_list):
    """Classic FedAvg"""
    coefs = np.array([w["coef"] for w in weights_list])
    intercepts = np.array([w["intercept"] for w in weights_list])
    avg_coef = np.mean(coefs, axis=0)
    avg_intercept = np.mean(intercepts)
    return {"coef": avg_coef.tolist(), "intercept": float(avg_intercept)}
