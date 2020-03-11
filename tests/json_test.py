import json
from pickle import dump, load
from typing import List, Any, Dict

from knowledge_resources.conclusion import Conclusion
from knowledge_resources.domain_case import DomainCase
from knowledge_resources.domain_context import DomainContext
from knowledge_resources.justification import Justification
from knowledge_resources.premise import Premise
from knowledge_resources.problem import Problem
from knowledge_resources.solution import Solution


def load_json(filename):
    with open(filename) as fh:
        obj = json.load(fh)
    return obj


def save_object(obj, file_name: str):
    with open(file_name, 'wb') as fh:
        dump(obj, fh)


def save_objects(objs: List[Any], file_name: str):
    with open(file_name, 'wb') as fh:
        for obj in objs:
            dump(obj, fh)


if __name__ == "__main__":
    f = load_json("test1.json")
    domain_cases = f["domain_case"]
    #print("Número de domain-cases en el JSON: ", len(domain_cases))
    #print("Toda la lista: ", domain_cases)

    new_domain_cases: List[DomainCase] = []
    for domain_case_dict in domain_cases:
        new_domain_case = DomainCase()
        new_domain_case.id = int(domain_case_dict["id"])
        new_domain_case.creation_date = domain_case_dict["creation_date"]

        new_problem = Problem()
        problem_dict = domain_case_dict["problem"]

        new_context = DomainContext()
        context_dict = problem_dict["context"]

        new_premises: Dict[int, Premise] = {}
        for premise_dict in context_dict["premises"]:
            new_premise = Premise()
            new_premise.id = int(premise_dict["id"])
            new_premise.name = premise_dict["name"]
            new_premise.content = premise_dict["content"]
            new_premises[new_premise.id] = new_premise

        new_context.premises = new_premises
        new_problem.context = new_context
        new_domain_case.problem = new_problem

        new_solutions: List[Solution] = []
        for solution_dict in domain_case_dict["solutions"]:
            new_solution = Solution()
            new_solution.times_used = int(solution_dict["times_used"])
            new_solution.value = solution_dict["value"]

            new_conclusion = Conclusion()
            conclusion_dict = solution_dict["conclusion"]
            new_conclusion.id = int(conclusion_dict["id"])
            new_conclusion.description = conclusion_dict["description"]
            new_solution.conclusion = new_conclusion

            new_solutions.append(new_solution)
        new_domain_case.solutions = new_solutions

        new_justification = Justification()
        justification_dict = domain_case_dict["justification"]
        new_justification.description = justification_dict["description"]
        new_domain_case.justification = new_justification

        new_domain_cases.append(new_domain_case)

    save_objects(new_domain_cases, "domain_cases_py.dat")

    fh = open("domain_cases_py.dat", 'rb')
    print("\n\n\nTodo el contenido del fichero:")
    count = 0
    while True:
        try:
            print(load(fh))
            count += 1
        except EOFError:
            print("Número de DomainCase en el fichero: ", count)
            break
    fh.close()
