# Neural network settings — reflection

> Final activity of this module. Keep under 700 words.

Hyperparameter effects

The neural-network surrogate I built this week used several hyperparameters that affected convergence, stability and predictive performance. The most important was the weight penalty set to 0.01, which nudges the network's weights gently towards zero during training. Lower values (1e-6) made the network memorise f8 with zero training error but predict wildly oscillating values in unmapped regions. Raising it to 1e-2 lifted training error slightly to 0.033 but produced smooth, sensible predictions outside the training data — far more useful for an extrapolation tool.

The shape of the network was equally important. I settled on two hidden layers of 16 and 8 neurons, around 200 weights total. With only 13-43 known points per function this is already over-parameterised; smaller architectures (8, 4) couldn't follow the surface, larger ones (64, 32) memorised the data instead of generalising.

The number of training iterations (`max_iter`, 5 000) controlled whether the network finished learning at all. At scikit-learn's default of 200, the loss was still trending downward at stop — meaning the network had not converged and its predictions were arbitrary. Lifting to 5 000 solved the issue.

The learning rate (default 1e-3) controls how large each weight-update step is. Higher rates speed convergence but risk overshooting; lower rates are slower but more stable. 

The activation function (ReLU) gives the network the ability to model curved surfaces. I briefly tried tanh: smoother gradients but trained slower on f8 with no fit improvement. 

Discrete vs continuous

The settings divide cleanly into three groups, and the type really does decide how each one should be tuned.

Continuous (real numbers) — learning rate, weight penalty, tolerance, dropout rate, momentum. These can be varied smoothly across a range, usually on a logarithmic scale, and respond well to gradient-based or Bayesian-Optimisation-style tuning.

Discrete-ordered (integers) — number of hidden layers, neurons per layer, batch size, training iterations, ensemble size. Integer-valued but ordered: 32 neurons is meaningfully larger than 16. These can use the same smooth methods provided candidate values are rounded back to whole numbers before training.

**Discrete-unordered (categorical)** — activation function (ReLU versus tanh versus sigmoid), optimiser type, loss function. There is no natural ordering — ReLU is not "less than" tanh, just different. Tuning requires either an exhaustive search across the options or finding a way to encode every choice.

This is the same trap that emerged on f8 in the capstone. The brief explicitly says two of the eight inputs are activation function and optimiser type, both encoded as numbers but actually categorical. Both my Gaussian Process and my neural network independently flagged x5 and x8 as ignored — i suspect because each was trying to fit a curve to what is really a series of discrete jumps.

Application to the capstone

My understanding of hyperparameter tuning will influence the neural network's role in the capstone in two ways. The network will continue to run in parallel to, the Gaussian Process. At 13-43 points per function the Gaussian Process is sample-efficient and gives calibrated uncertainty essentially for free. The network's strength is different — it extrapolates trends into unmapped regions where the Gaussian Process reverts to its prior mean. I will keep the network small, maintain a moderate weight penalty, and resist adding complexity until there is more data.

The Bayesian Optimisation approach used in the course could be applied directly to tuning the network. Each "query" would train a network with one candidate combination (learning rate, weight penalty, hidden-layer sizes) and report leave-one-out cross-validation error as the score. Similar to the Gaussian Process surrogate plus acquisition function, this could be applied to tuning the parameters, especially since one fit takes seconds.
