import numpy as np
import matplotlib.pyplot as plt

# AND gate dataset
X = np.array([
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1]
])
y = np.array([0, 0, 0, 1])

# Parameters
alpha = 1.0           # Larger learning rate for faster separation
epochs = 10
n_samples, n_features = X.shape

# Initialize weights and bias
weights = np.random.randn(n_features)
bias = np.random.randn()

# Plot setup
plt.ion()
fig, ax = plt.subplots()
colors = ['red' if label == 0 else 'blue' for label in y]
ax.scatter(X[:, 0], X[:, 1], c=colors, edgecolors='k', s=100)
ax.set_xlim(-0.2, 1.2)
ax.set_ylim(-0.2, 1.2)
ax.set_xlabel("x1")
ax.set_ylabel("x2")
line = None

def plot_decision_boundary(w, b, epoch):
    global line
    ax.set_title(f'Decision Boundary - Epoch {epoch + 1}')
    x_vals = np.array([0.2, 1.2])
    y_vals = np.abs(x_vals * w + b)
    y_vals[0] = np.clip(y_vals[0], 1, 1.2)  # Ensure y values are within bounds
    y_vals[1] = np.clip(y_vals[1], 0.2, 0.9)  # Ensure y values are within bounds
    print(f"Epoch {epoch + 1}: Weights: {w}, Bias: {b}")
    # print(x_vals, y_vals)
    # Remove previous line
    if line is not None:
        line.remove()
    line, = ax.plot(x_vals, y_vals, 'k--', linewidth=2)
    plt.draw()
    plt.pause(0.1)

# Training loop
weights_error = []
for epoch in range(epochs):
    for i in range(n_samples):
        xi = X[i]
        target = y[i]
        output = np.dot(weights, xi) + bias
        pred = 1 if output >= 0.5 else 0
        error = target - pred

        weights_error.append([weights[0], weights[1], target-output])
        weights += alpha * xi * error
        bias += alpha * error

    plot_decision_boundary(weights.copy(), bias, epoch)

plt.ioff()
plt.show()

# Final predictions
print("Final Weights:", weights)
print("Final Bias:", bias)
print("\nPredictions:")
for xi in X:
    output = np.dot(weights, xi) + bias
    pred = 1 if output >= 0.5 else 0
    print(f"Input: {xi}, Prediction: {pred}")

# print(weights_error)

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata

# Raw data
data = np.array(weights_error)

# Extract columns
w0 = data[:, 0]
w1 = data[:, 1]
error = data[:, 2]

# Create a grid for surface plot
grid_w0, grid_w1 = np.meshgrid(
    np.linspace(min(w0), max(w0), 50),
    np.linspace(min(w1), max(w1), 50)
)

# Interpolate error values to fit the mesh grid
grid_error = griddata((w0, w1), error, (grid_w0, grid_w1), method='cubic')

# Plotting the 3D mesh
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')
surface = ax.plot_surface(grid_w0, grid_w1, grid_error, cmap='viridis', edgecolor='k', alpha=0.8)

ax.set_title("3D Mesh Plot of Error over Weight Space")
ax.set_xlabel("Weight w0")
ax.set_ylabel("Weight w1")
ax.set_zlabel("Error")
fig.colorbar(surface, shrink=0.5, aspect=10, label='Error')

plt.tight_layout()
plt.show()

