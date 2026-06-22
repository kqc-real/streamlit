# Overarching Learning Objectives: Decision Trees

## Transparent supervised prediction
**Learners can treat decision trees as interpretable supervised models for classification and regression.**

This cluster establishes the basic model concept: a decision tree predicts by following a sequence of feature-based tests from the root to a leaf. Learners distinguish between classification outputs, regression outputs, and the role of terminal nodes.

It also builds the foundation for reading trees as white-box models whose predictions can be traced through explicit decision paths.

---

## Node interpretation and probability estimation
**Learners can read node-level information and connect it to model predictions.**

This cluster focuses on the practical interpretation of `samples`, `value`, class counts, and leaf proportions. Learners use these quantities to explain why a classification tree predicts a particular class.

The cluster also covers how decision trees estimate class probabilities from the empirical distribution of samples within a leaf.

---

## Split criteria and CART training
**Learners can apply the core logic of split selection in classification and regression trees.**

This cluster links impurity measures, weighted child-node quality, and greedy split selection. Learners distinguish Gini impurity, entropy, and mean squared error as criteria used in different decision-tree settings.

The competency includes recognizing CART as a locally optimizing algorithm that grows binary trees recursively without searching all possible complete tree structures.

---

## Regularization and generalization
**Learners can select structural constraints that reduce overfitting in decision trees.**

This cluster develops practical judgment about model complexity. Learners connect deep trees, small leaves, and train-test gaps with overfitting, then choose suitable constraints such as `max_depth`, `min_samples_leaf`, `min_samples_split`, and `max_features`.

It also includes post-pruning as a complementary regularization strategy for removing weak or statistically unsupported structure.

---

## Regression with decision trees
**Learners can transfer tree-based reasoning from class prediction to numerical prediction.**

This cluster covers how regression trees store numerical predictions in leaves and how CART chooses splits for regression. Learners compute leaf predictions and recognize mean squared error as the relevant split objective.

The emphasis is on seeing regression trees as structurally similar to classification trees but governed by a different prediction target and optimization criterion.

---

## Computational scalability
**Learners can reason about the computational behavior of decision trees during training and prediction.**

This cluster separates prediction cost from training cost. Learners recognize why prediction is fast in a reasonably balanced tree and why training becomes more expensive as the number of samples or features increases.

The competency supports informed choices when applying decision trees to larger datasets or high-dimensional feature spaces.

---

## Feature-space geometry and preprocessing
**Learners can analyze how feature orientation affects axis-aligned tree splits.**

This cluster addresses a structural limitation of standard decision trees: their preference for axis-aligned decision boundaries. Learners recognize why rotated or diagonal class boundaries can lead to unnecessarily complex tree structures.

It also covers the use of scaling and PCA as a possible preprocessing strategy for rotating the feature space into a representation that may better match tree splits.

---

## Variance and ensemble stabilization
**Learners can justify ensemble methods as a remedy for high-variance decision trees.**

This cluster focuses on the instability of individual trees under small data or training changes. Learners connect stochastic training, unfixed random seeds, and high variance with the motivation for Random Forests.

The cluster culminates in majority voting or prediction aggregation as a mechanism for stabilizing many individually variable trees.

---

# Detailed Learning Objectives

In the context of **Decision Trees**, this question set helps you achieve the following detailed learning objectives:

### Reproduction

**You can ...**

1. identify decision trees as supervised models for classification and regression.
2. define a leaf as the terminal prediction node of a decision tree.
3. state the condition for zero Gini impurity in a node.
4. identify `max_depth` as the hyperparameter for limiting tree depth.
5. describe the usual leaf prediction in a regression tree.

### Application

**You can ...**

1. recognize path-based prediction in a trained decision tree.
2. interpret `samples` and `value` attributes in a classification node.
3. determine a class probability from leaf-level class counts.
4. select the CART split rule based on weighted child-node impurity.
5. recognize the greedy nature of CART from local split selection.
6. select the correct comparison between Gini impurity and entropy.
7. select regularization changes for an overfitted decision tree.
8. determine the effect of increasing `min_samples_leaf`.
9. classify train-test score patterns in a regularized tree comparison.
10. recognize post-pruning from statistically weak purity gains.
11. select `max_features` as the feature constraint during split search.
12. select `min_samples_split` as the stopping condition for small nodes.
13. determine the mean prediction for a regression leaf.
14. select weighted mean squared error as the CART regression split criterion.
15. recognize root-to-leaf traversal as the basis of fast prediction.
16. determine the CART training-time effect of doubling the feature count.
17. recognize axis-aligned splitting as the cause of complex rotated-data boundaries.
18. select PCA-based feature rotation for tree-friendly split geometry.
19. recognize unfixed `random_state` as a source of non-reproducible trees.
20. select prediction aggregation as a Random Forest variance-reduction mechanism.

### Analysis

**You can ...**

1. analyze PCA-transformed feature space as a remedy for diagonal decision boundaries.
2. derive Gini impurity for a two-class node with equal proportions.
3. diagnose overfitting from deep trees with tiny leaves.
4. assess CART training-time growth under a tenfold sample increase.
5. justify majority voting as variance reduction in tree ensembles.
