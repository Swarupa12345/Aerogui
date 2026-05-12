import matplotlib.pyplot as plt


def prediction_plot(actual, predicted):
    plt.figure(figsize=(6,4))

    plt.plot(actual, label='Actual', marker='o')
    plt.plot(predicted, label='Predicted', marker='x')

    plt.title("Prediction Accuracy")
    plt.xlabel("Sample")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("prediction_plot.png")
    plt.close()