from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from utils.metrics import custom_roc_auc
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import GridSearchCV


def define_models():
    """Return a dictionary of models."""
    return {
        "Random Forest": RandomForestClassifier(
            random_state=1234,
        ),
        "KNN": KNeighborsClassifier(
        ),
        "MLP": MLPClassifier(
            random_state=1234,
        ),
    }


def define_param_grid():
    """Return a dictionary of model names and their parameter grids."""
    return {
        "Random Forest": {
            "n_estimators": [10, 50, 100, 200],
            "max_depth": [5, 10, 20, None],
            "max_features": ["sqrt", "log2", None],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
            "bootstrap": [True, False],
        },
        "KNN": {
            "n_neighbors": [3, 5, 10, 15, 20],
            "weights": ["uniform", "distance"],
            "algorithm": ["auto", "ball_tree", "kd_tree", "brute"],
            "leaf_size": [10, 30, 50],
            "p": [1, 2],  # 1 for Manhattan distance, 2 for Euclidean
        },
        "MLP": {
            "hidden_layer_sizes": [(50,), (100,), (100, 50), (150, 100, 50)],
            "solver": ["adam", "sgd", "lbfgs"],
            "activation": ["relu", "tanh", "logistic"],
            "alpha": [0.0001, 0.001, 0.01, 0.1],  # Regularization term
            "learning_rate": ["constant", "invscaling", "adaptive"],
            "max_iter": [500, 1000, 2000],
        },
    }


def train_and_evaluate(models, X_train, X_test, y_train, y_test,
                       from_loaded=False):
    """Train models, evaluate accuracy, ROC, and AUC."""
    results = {}
    trained_models = {}

    for name, model in models.items():
        if not from_loaded:
            model.fit(X_train, y_train)
        trained_models[name] = model

        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        results[name] = {"accuracy": acc}

        print(f"--- {name} ---")
        print(classification_report(y_test, y_pred))

        y_scores = model.predict_proba(X_test)[:, 1]
        fpr, tpr, auc = custom_roc_auc(y_test, y_scores)

        results[name]["fpr"] = fpr
        results[name]["tpr"] = tpr
        results[name]["auc"] = auc

    return results, trained_models


def tune_models(models, param_grids, X_train, y_train):
    """
    Tune models using GridSearchCV and return the best models with their
    parameters.

    Parameters:
    - models: Dictionary of model names and instances.
    - param_grids: Dictionary of model names and their parameter grids.
    - X_train: Training data features.
    - y_train: Training data labels.

    Returns:
    - best_models: Dictionary of model names and their tuned instances.
    """
    best_models = {}

    for name, model in models.items():
        if name in param_grids:
            print(f"Tuning {name}...")
            grid_search = GridSearchCV(
                model, param_grids[name], scoring='roc_auc', cv=3, n_jobs=-1)
            grid_search.fit(X_train, y_train)
            best_models[name] = grid_search.best_estimator_
            print(f"Best parameters for {name}: {
                grid_search.best_params_}")
        else:
            # No tuning grid provided, use the original model
            best_models[name] = model

            return best_models
