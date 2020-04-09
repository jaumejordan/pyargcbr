from dataclasses import dataclass

from knowledge_resources.argument_justification import ArgumentJustification
from knowledge_resources.argument_problem import ArgumentProblem
from knowledge_resources.argument_solution import ArgumentSolution
from knowledge_resources.case import Case


@dataclass
class ArgumentCase(Case):
    problem: ArgumentProblem = ArgumentProblem()
    solutions: ArgumentSolution = ArgumentSolution()  # Keeping the plural is not accurate. It is for code coherence
    justification: ArgumentJustification = ArgumentJustification()
    times_used: int = 0

    def __str__(self):
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
