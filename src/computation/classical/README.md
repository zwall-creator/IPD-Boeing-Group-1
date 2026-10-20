# Classical Solvers

### Input
Describe to the solver what a valid placement looks like and what makes a placement better.

1. Variables: what the solver is allowed to choose
2. Constraints: rules that a solution must follow
3. Objective: the number to minimize or maximize

### OR-Tools

- CpModel is a container where you declare variables, constraints, and the objective for the solver.
- CpSolver takes the finished model and actually searches for a solution.
- CP-SAT only works with integers so any float values must be scaled. Remember to scale back down when reading results.
- Can set a max time to search and the solver will search for that long returning the best solution found in that time (this can be a user input)


### Specific to our problem

- Our nodes store directed connections but it may be useful to convert them to an undirected single connection for the solver.
- The way that the problem is going to be fed into the solver initially is to have it place a security device on a link and then the post processing will update the network to to create new links between the old two nodes to the device (note that this will not allow for chained device placement, maybe a feature down the line)
- The solver will need a security level expression which calculates the final security level for each node.
- The goal of the solver is to minimize the sum of the gaps between each nodes risk level and security level (gap = risk - security)
- For each link a list of which nodes will be protected if a security device is placed on it will need to be precomputed (discuss with zak, although I think this should be relatively simple)
- We are staring with a relatively simple problem but I believe it should be easy to modify in the future to update it to actually be RCPSP or RCPSP adjacent


