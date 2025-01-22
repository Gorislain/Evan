import numpy as np
import mne
from mne.datasets import eegbci
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import random


def activation(x, act_type):
    if act_type == "relu":
        return np.maximum(0, x)
    elif act_type == "sigmoid":
        return 1 / (1 + np.exp(-x))
    elif act_type == "tanh":
        return np.tanh(x)
    elif act_type == "leaky_relu":
        return x if x > 0 else 0.01 * x
    return np.maximum(0, x)


def activation_derivative(x, act_type):
    if act_type == "relu":
        return 1 if x > 0 else 0
    elif act_type == "sigmoid":
        sig = 1 / (1 + np.exp(-x))
        return sig * (1 - sig)
    elif act_type == "tanh":
        return 1 - np.tanh(x) ** 2
    elif act_type == "leaky_relu":
        return 1 if x > 0 else 0.01


def weight_factory(list_of_char):
    list_of_neurons = [list_of_char[0]] + list_of_char[1:] + [1]
    weights = []
    for i in range(len(list_of_neurons) - 1):
        layer_weights = [
            [random.uniform(-0.1, 0.1) for _ in range(list_of_neurons[i])]
            for _ in range(list_of_neurons[i + 1])
        ]
        weights.append(layer_weights)
    return weights


def forward_pass(weights, input_data, activ):
    layer_outputs = [input_data]
    for layer_weights in weights:
        input_data = [
            activation(sum(w * x for w, x in zip(neuron_weights, input_data)), activ)
            for neuron_weights in layer_weights
        ]
        layer_outputs.append(input_data)
    return layer_outputs


def backward_pass(weights, layer_outputs, expected_output, learning_rate, activ):
    deltas = []
    output_error = [expected_output - layer_outputs[-1][0]]
    deltas.append([e * activation_derivative(o, activ) for e, o in zip(output_error, layer_outputs[-1])])
    for i in range(len(weights) - 2, -1, -1):
        layer_delta = []
        for j, neuron_weights in enumerate(weights[i]):
            error = sum(d * w[j] for d, w in zip(deltas[0], weights[i + 1]))
            layer_delta.append(error * activation_derivative(layer_outputs[i + 1][j], activ))
        deltas.insert(0, layer_delta)
    for i, layer_weights in enumerate(weights):
        for j, neuron_weights in enumerate(layer_weights):
            for k in range(len(neuron_weights)):
                neuron_weights[k] += learning_rate * deltas[i][j] * layer_outputs[i][k]


def train_network(weights, inputs, outputs, epochs, learning_rate, activ, batch_size):
    for epoch in range(epochs):
        total_loss = 0
        for batch_start in range(0, len(inputs), batch_size):
            batch_inputs = inputs[batch_start:batch_start + batch_size]
            batch_outputs = outputs[batch_start:batch_start + batch_size]

            for input_data, expected_output in zip(batch_inputs, batch_outputs):
                layer_outputs = forward_pass(weights, input_data, activ)
                loss = (expected_output[0] - layer_outputs[-1][0]) ** 2
                total_loss += loss
                backward_pass(weights, layer_outputs, expected_output, learning_rate, activ)

        avg_loss = float(total_loss) / len(inputs)
        print(f"Эпоха {epoch + 1}: Потеря = {avg_loss:.4f}")
    return weights


def predict(weights, inputs, activ):
    predictions = []
    for input_data in inputs:
        layer_outputs = forward_pass(weights, input_data, activ)
        output_value = layer_outputs[-1][0]
        predictions.append(int(round(output_value.item())))
    return predictions


def calculate_accuracy(predictions, actuals):
    correct = sum(p == a for p, a in zip(predictions, actuals))
    accuracy = correct / len(actuals)
    return accuracy


subject = 1
runs = [6, 10]
freq_range = (7, 30)
data_path = eegbci.load_data(subject, runs, path="./eeg_data")
raw_list = [mne.io.read_raw_edf(file, preload=True) for file in data_path]
raw = mne.concatenate_raws(raw_list)
mne.datasets.eegbci.standardize(raw)
raw.notch_filter(freqs=50)
raw.filter(l_freq=freq_range[0], h_freq=freq_range[1])
events, event_id = mne.events_from_annotations(raw)
epochs = mne.Epochs(raw, events, event_id, tmin=0, tmax=2, baseline=None, preload=True)

X = epochs.get_data().reshape(len(epochs), -1)
y = epochs.events[:, -1] - 1

scaler = StandardScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

train_inputs = [list(row) for row in X_train]
train_outputs = [[val] for val in y_train]
test_inputs = [list(row) for row in X_test]

neuron_character = [X_train.shape[1], 10, 8]
weights = weight_factory(neuron_character)

batch_size = 32
weights = train_network(weights, train_inputs, train_outputs, epochs=10, learning_rate=0.01, activ="relu",
                        batch_size=batch_size)

test_predictions = predict(weights, test_inputs, activ="relu")
accuracy = calculate_accuracy(test_predictions, y_test)
print(f"Точность модели на тестовых данных: {accuracy * 100:.2f}%")
