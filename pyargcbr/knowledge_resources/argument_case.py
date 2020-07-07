from dataclasses import dataclass

from .argument_justification import ArgumentJustification
from .argument_problem import ArgumentProblem
from .argument_solution import ArgumentSolution
from .case import Case


@dataclass
class ArgumentCase(Case):
    """Implementation of the concept ArgumentCase"""
    times_used: int = 0
    problem: ArgumentProblem = ArgumentProblem()
    solutions: ArgumentSolution = ArgumentSolution()
    justification: ArgumentJustification = ArgumentJustification()

    def __init__(self, arg_id: int, creation_date: str, problem: ArgumentProblem,
                 solution: ArgumentSolution,
                 justification: ArgumentJustification, times_used: int = 0):
        """ArgumentCase is a specialization of Case

        Args:
            problem (ArgumentProblem): Argument cases problems are ArgumentProblem
            solution (ArgumentSolution): The argument cases have only one solution
            justification (ArgumentJustification): Argument cases solutions have ArgumentSolutions
        """
        super().__init__(id=arg_id, creation_date=creation_date, problem=problem, solutions=solution,
                         justification=justification)
        self.times_used = times_used

    def __str__(self):
        """Default 'to string' method rewritten

        Returns:
            str: A descriptive str of the ArgumentCase
        """
        st = "id: " + str(self.id) + " creationDate: " + self.creation_date + "\n"
        st += "Domain context. Premises:\n"
        premises = self.problem.context.premises
        for p in premises.keys():
            st += "\t ID: " + str(p)
            st += " Content: " + str(premises[p])

        st += "\nSocial context. \n"
        pro = self.problem.social_context.proponent
        st += "Proponent ID: " + str(pro.id) + " name: " + pro.name + " role: " + pro.role + "\n"

        op = self.problem.social_context.opponent
        st += "Proponent ID: " + str(op.id) + " name: " + op.name + " role: " + op.role + "\n"

        st += "Dependency Relation: " + str(self.problem.social_context.relation) + "\n"

        return st
