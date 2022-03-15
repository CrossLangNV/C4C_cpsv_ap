import numpy as np
from numpy import ndarray
from scipy.stats import sem
from sklearn.metrics import f1_score

'''
Collection of scoring functions. micro F1, RP@k, nDCG@k.
'''


def calculate_micro_f1_score(true_labels: ndarray, preds_proba: ndarray, threshold: int = 0.5):
    '''
    Micro f1_score.
    
    :param true_labels: numpy array of shape [ n_samples, n_labels ] with the one hot encoding gold labels.
    :param preds_proba: numpy array of shape [ n_samples, n_labels ] with the predicted probability for each label.
    :param threshold: int, threshold used.
    '''

    preds_labels = (preds_proba >= threshold) * 1
    return f1_score(true_labels, preds_labels, average='micro')


def ranking_precision_score(y_true, y_score, k=10):
    """Precision at rank k
    Parameters
    ----------
    y_true : array-like, shape = [n_labels]
        Ground truth (true relevance labels).
    y_score : array-like, shape = [n_labels]
        Predicted scores.
    k : int
        Rank.
    Returns
    -------
    precision @k : float
    """

    unique_y = np.unique(y_true)

    if len(unique_y) > 2:
        raise ValueError("Only supported for two relevance levels.")

    pos_label = unique_y[1]
    n_pos = np.sum(y_true == pos_label)

    order = np.argsort(y_score)[::-1]
    y_true = np.take(y_true, order[:k])
    n_relevant = np.sum(y_true == pos_label)

    # Divide by min(n_pos, k) such that the best achievable score is always 1.0.
    return float(n_relevant) / min(n_pos, k)


def precision_at_k(y_true, y_score, k):
    sm = 0
    for i in range(y_true.shape[0]):
        sm += ranking_precision_score(y_true[i], y_score[i], k=k)
    return sm / y_true.shape[0]


def dcg_score(y_true, y_score, k=10, gains="exponential"):
    """Discounted cumulative gain (DCG) at rank k
    Parameters
    ----------
    y_true : array-like, shape = [n_labels]
        Ground truth (true relevance labels).
    y_score : array-like, shape = [n_labels]
        Predicted scores.
    k : int
        Rank.
    gains : str
        Whether gains should be "exponential" (default) or "linear".
    Returns
    -------
    DCG @k : float
    """
    order = np.argsort(y_score)[::-1]
    y_true = np.take(y_true, order[:k])

    if gains == "exponential":
        gains = 2 ** y_true - 1
    elif gains == "linear":
        gains = y_true
    else:
        raise ValueError("Invalid gains option.")

    # highest rank is 1 so +2 instead of +1
    discounts = np.log2(np.arange(len(y_true)) + 2)
    return np.sum(gains / discounts)


def ndcg_score(y_true, y_score, k=10, gains="exponential"):
    """Normalized discounted cumulative gain (NDCG) at rank k
    Parameters
    ----------
    y_true : array-like, shape = [n_labels]
        Ground truth (true relevance labels).
    y_score : array-like, shape = [n_labels]
        Predicted scores.
    k : int
        Rank.
    gains : str
        Whether gains should be "exponential" (default) or "linear".
    Returns
    -------
    NDCG @k : float
    """
    best = dcg_score(y_true, y_true, k, gains)
    actual = dcg_score(y_true, y_score, k, gains)
    return actual / best


def ndcg_at_k(y_true, y_score, k, gains="exponential"):
    sm = 0
    for i in range(y_true.shape[0]):
        sm += ndcg_score(y_true[i], y_score[i], k=k, gains=gains)
    return sm / y_true.shape[0]


def default_rprecision_score(y_true, y_score):
    """R-Precision
    Parameters
    ----------
    y_true : array-like, shape = [n_samples]
        Ground truth (true relevant labels).
    y_score : array-like, shape = [n_samples]
        Predicted scores.
    Returns
    -------
    precision @k : float
    """
    unique_y = np.unique(y_true)

    if len(unique_y) == 1:
        raise ValueError("The score cannot be approximated.")
    elif len(unique_y) > 2:
        raise ValueError("Only supported for two relevant levels.")

    pos_label = unique_y[1]
    n_pos = np.sum(y_true == pos_label)

    order = np.argsort(y_score)[::-1]
    y_true = np.take(y_true, order[:n_pos])
    n_relevant = np.sum(y_true == pos_label)

    # Divide by n_pos such that the best achievable score is always 1.0.
    return float(n_relevant) / n_pos


def mean_rprecision(y_true, y_score):
    """Mean r-precision
    Parameters
    ----------
    y_true : array-like, shape = [n_samples]
        Ground truth (true relevant labels).
    y_score : array-like, shape = [n_samples]
        Predicted scores.
    Returns
    -------
    mean r-precision : float
    """

    p_ks = []
    for y_t, y_s in zip(y_true, y_score):
        if np.sum(y_t == 1):
            p_ks.append(default_rprecision_score(y_t, y_s))

    return np.mean(p_ks), sem(p_ks)
