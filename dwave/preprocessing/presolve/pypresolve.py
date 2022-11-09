# Copyright 2022 D-Wave Systems Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import dimod

from dwave.preprocessing.presolve.cypresolve import cyPresolver

__all__ = ['Presolver', 'InfeasibleModelError']


class InfeasibleModelError(ValueError):
    pass


class Presolver(cyPresolver):
    """Presolver for constrained quadratic models.

    The model held by this class to represent the instantiating constrained
    quadratic model (CQM) is index-labeled. This is because presolve may remove,
    add, change the type of, and substitute variables. Consequently, while the
    models remain mathematically equivalent, variables of the original and reduced
    CQMs may not have a direct relationship.

    Args:
        cqm: A :class:`dimod.ConstrainedQuadraticModel`.
        move: If ``True``, the original CQM is cleared and its contents are moved
            to the presolver. This is useful for large models where memory is a concern.

    Example:

        This example reduces an implicitly fixed constraint.

        >>> import dimod
        >>> from dwave.preprocessing import Presolver

        Create a simple CQM with one variable fixed by bounds.

        >>> cqm = dimod.ConstrainedQuadraticModel()
        >>> i = dimod.Integer('i', lower_bound=-5, upper_bound=5)
        >>> j = dimod.Integer('j', lower_bound=5, upper_bound=10)
        >>> cqm.set_objective(i + j)
        >>> c0 = cqm.add_constraint(j <= 5)  # implicitly fixes 'j'

        Run presolve with default settings.

        >>> presolver = Presolver(cqm)
        >>> presolver.load_default_presolvers()
        >>> presolver.apply()

        The model is reduced.

        >>> reduced_cqm = presolver.detach_model()
        >>> reduced_cqm.num_variables()
        1
        >>> reduced_cqm.num_constraints()
        0

    """
    # include this for the function signature
    def __init__(self, cqm: dimod.ConstrainedQuadraticModel, *, move: bool = False):
        super().__init__(cqm, move=move)

    def apply(self):
        try:
            super().apply()
        except RuntimeError as err:
            if str(err) == 'infeasible':
                # checking based on the string is not ideal, but Cython is
                # not-so-good at custom exceptions
                raise InfeasibleModelError("given CQM is infeasible") from err
            raise err
