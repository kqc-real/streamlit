# Overarching learning objectives: Support Vector Machines (SVM)

## 1) Large-margin intuition and decision geometry
**Frame SVMs as maximum-margin classifiers.**

You build a precise geometric model of how SVMs choose separating hyperplanes and why maximizing the margin often improves generalization.

---

## 2) Support vectors and prediction behavior
**Explain which data points influence an SVM and how predictions are produced.**

You connect the decision rule to the subset of training points that matter (support vectors) and predict when additional points will (not) change the boundary.

---

## 3) Preprocessing and feature scaling
**Prevent scale artifacts through appropriate preprocessing.**

You detect unit/range mismatches and implement scaling correctly (e.g., via pipelines) to avoid distorted dot products or distances.

---

## 4) Soft margin, regularization, and loss choices
**Select C and loss variants to balance robustness and fit.**

You tune the violation penalty and choose between hinge-style losses to handle noise, outliers, and under/overfitting patterns.

---

## 5) Kernels and kernel validity
**Use kernels as implicit feature mappings and validate kernel suitability.**

You interpret kernels as inner products in feature space, match algebraic forms to kernel families, and apply validity criteria that keep optimization well-defined.

---

## 6) Hyperparameters for non-linear SVMs
**Control model flexibility via γ, coef0, and related settings.**

You relate hyperparameters to boundary smoothness/complexity and select adjustments aligned with observed error patterns.

---

## 7) Scalability, formulation choices, and SVR
**Choose implementations that fit data size and task type.**

You justify when to prefer primal vs dual viewpoints, linear/SGD-based training for large data, and SVR settings that control the ε-tube and support vectors.

---

# Detailed learning objectives

In the context of **Support Vector Machines (SVM)**, this question set should help you achieve the following detailed learning objectives:

### Reproduction

**You can …**

1. state the geometric training objective of a linear SVM as maximizing the margin.
2. identify support vectors as the points that determine the decision boundary.
3. define a kernel as an inner product in an implicit feature space.
4. recall the typical default loss associated with LinearSVC in common ML libraries.

### Application

**You can …**

1. recognize why feature scaling is important before training an SVM.
2. determine the typical effect of decreasing C in a soft-margin SVM.
3. determine how squared hinge loss reacts to outliers compared with hinge loss.
4. determine the typical effect of increasing γ in an RBF-kernel SVM.
5. select an SGD-based hinge-loss classifier for very large, online, linear learning settings.
6. determine the effect of decreasing ε in SVR on the number of support vectors.
7. determine that changing only b (with fixed w) shifts the hyperplane without changing margin width.
8. complete a preprocessing pipeline by inserting StandardScaler before a linear SVM.
9. select a soft-margin SVM with low C to improve robustness under outliers.
10. determine the effect of adding correctly classified points far from the margin on the decision boundary.
11. select a scaling step to reduce scale-related issues in an RBF SVC workflow.
12. interpret a slack variable as the amount of margin violation for a training point.
13. determine the role of coef0 in a polynomial kernel.
14. apply the sign rule of the decision score s = w·x + b to predict the positive class.
15. select standardization when features have incompatible units or ranges.
16. select hinge loss over squared hinge loss when strong outliers are present.
17. select a linear kernel as a sensible first baseline choice.

### Structural Analysis

**You can …**

1. justify choosing the dual formulation for a linear SVM when m is smaller than n.
2. analyze which points typically have non-zero α at the optimum in the dual SVM.
3. derive the matching kernel family from an inner-product identity such as (aᵀb)².
4. diagnose how to reduce underfitting in a linear soft-margin SVM via a C adjustment.
5. derive a paired adjustment of C and γ to reduce overfitting in an RBF SVM.
6. justify the PSD Gram-matrix requirement as a key condition for a valid Mercer kernel.
7. analyze why prediction time in a kernel SVM depends mainly on the number of support vectors.
8. evaluate the scalability trade-off between kernel SVC and LinearSVC on large datasets.
9. determine the effect of increasing ε in SVR on the number of support vectors.
