from poketactician.MOACO import MOACO
from timeit import Timer
from poketactician.MOACO import MOACO
from poketactician.Colony import Colony, Colony
from poketactician.glob_var import pokPreFilter, alpha, beta, Q, rho
from poketactician.objectives import (
    attack_obj_fun,
    team_coverage_fun,
    self_coverage_fun,
)

pokList = pokPreFilter
attackObjFun = lambda team: attack_obj_fun(team, pokList)
objectiveFuncs = []
objectiveFuncs.append((attackObjFun, Q, 0.1))
t = Timer(
    lambda: MOACO(
        Colony,
        400,
        objectiveFuncs,
        pokList,
        alpha,
        beta,
    ).optimize(iters=20, time_limit=None)
)
print(t.timeit(10))
