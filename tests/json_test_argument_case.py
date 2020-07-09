import json
from pickle import dump, load
from typing import List, Any, Dict

from loguru import logger

from pyargcbr.knowledge_resources.arg_node import ArgNode
from pyargcbr.knowledge_resources.argument_case import ArgumentCase
from pyargcbr.knowledge_resources.argument_justification import ArgumentJustification
from pyargcbr.knowledge_resources.argument_problem import ArgumentProblem
from pyargcbr.knowledge_resources.argument_solution import ArgumentSolution
from pyargcbr.knowledge_resources.argumentation_scheme import ArgumentationScheme
from pyargcbr.knowledge_resources.author import Author
from pyargcbr.knowledge_resources.conclusion import Conclusion
from pyargcbr.knowledge_resources.dialogue_graph import DialogueGraph
from pyargcbr.knowledge_resources.domain_context import DomainContext
from pyargcbr.knowledge_resources.premise import Premise
from pyargcbr.knowledge_resources.social_context import SocialContext
from pyargcbr.knowledge_resources.social_entity import SocialEntity
from pyargcbr.knowledge_resources.valpref import ValPref


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
    f = load_json("test_argument_case2.json")
    argument_cases = f["argument_case"]
    new_argument_cases = []
    count = 0
    for argument_case_dict in argument_cases:
        new_id = argument_case_dict["id"]
        new_creation_date = argument_case_dict["creation_date"]

        #####################################################################
        # ArgumentProblems

        new_problem = ArgumentProblem()
        problem_dict = argument_case_dict["problem"]

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

        new_social_context = SocialContext()
        social_context_dict = problem_dict["social_context"]

        new_proponent = SocialEntity()
        proponent_dict = social_context_dict["proponent"]
        new_proponent.id = proponent_dict["id"]
        new_proponent.name = proponent_dict["name"]
        new_proponent.role = proponent_dict["role"]
        new_proponent.norms = proponent_dict["norms"]

        new_val_pref = ValPref()
        val_pref_dict = proponent_dict["val_pref"]
        new_val_pref.values = val_pref_dict["values"]
        new_proponent.valpref = new_val_pref

        new_opponent = SocialEntity()
        opponent_dict = social_context_dict["opponent"]
        new_opponent.id = opponent_dict["id"]
        new_opponent.name = opponent_dict["name"]
        new_opponent.role = opponent_dict["role"]
        new_opponent.norms = opponent_dict["norms"]

        new_val_pref = ValPref()
        val_pref_dict = opponent_dict["val_pref"]
        new_val_pref.values = val_pref_dict["values"]
        new_opponent.valpref = new_val_pref

        new_group = SocialEntity()
        group_dict = social_context_dict["group"]
        new_group.id = group_dict["id"]
        new_group.name = group_dict["name"]
        new_group.role = group_dict["role"]
        new_group.norms = group_dict["norms"]

        new_val_pref = ValPref()
        val_pref_dict = group_dict["val_pref"]
        new_val_pref.values = val_pref_dict["values"]
        new_group.valpref = new_val_pref

        new_social_context.proponent = new_proponent
        new_social_context.opponent = new_opponent
        new_social_context.group = new_group
        new_social_context.relation = social_context_dict["relation"]

        new_problem.social_context = new_social_context
        #####################################################################
        # ArgumentSolutions

        new_solution = ArgumentSolution()
        solution_dict = argument_case_dict["solution"]
        new_solution.times_used = solution_dict["times_used"]
        new_solution.value = solution_dict["value"]
        new_conclusion = Conclusion()
        conclusion_dict = solution_dict["conclusion"]
        new_conclusion.id = conclusion_dict["id"]
        new_conclusion.description = conclusion_dict["description"]
        new_solution.conclusion = new_conclusion
        new_solution.argument_type = solution_dict["argument_type"]

        new_solution.dist_premises = []
        dist_premises_dicts = solution_dict["dist_premises"]
        for dist_premise_dict in dist_premises_dicts:
            new_premise = Premise()
            new_premise.id = dist_premise_dict["id"]
            new_premise.name = dist_premise_dict["name"]
            new_premise.content = dist_premise_dict["content"]
            new_solution.dist_premises.append(new_premise)

        new_solution.presumptions = []
        presumptions_dicts = solution_dict["presumptions"]
        for presumptions_dict in presumptions_dicts:
            new_premise = Premise()
            new_premise.id = presumptions_dict["id"]
            new_premise.name = presumptions_dict["name"]
            new_premise.content = presumptions_dict["content"]
            new_solution.presumptions.append(new_premise)

        new_solution.exceptions = []
        exceptions_dicts = solution_dict["exceptions"]
        for exceptions_dict in exceptions_dicts:
            new_premise = Premise()
            new_premise.id = exceptions_dict["id"]
            new_premise.name = exceptions_dict["name"]
            new_premise.content = exceptions_dict["content"]
            new_solution.exceptions.append(new_premise)

        new_solution.counter_examples_dom_case_id = solution_dict["counter_examples_dom_case_id_list"]
        new_solution.counter_examples_arg_case_id = solution_dict["counter_examples_arg_case_id_list"]

        #####################################################################
        # ArgumentSJustifications

        new_justification = ArgumentJustification()
        justification_dict = argument_case_dict["justification"]
        new_justification.description = justification_dict["description"]
        new_justification.domain_cases_ids = justification_dict["domain_cases_ids"]
        new_justification.argument_cases_ids = justification_dict["argument_cases_ids"]

        new_justification.schemes = []
        schemes_dicts = justification_dict["schemes"]
        for schemes_dict in schemes_dicts:
            new_scheme = ArgumentationScheme()
            new_scheme.id = schemes_dict["id"]
            new_scheme.arg_title = schemes_dict["arg_title"]
            new_scheme.creation_date = schemes_dict["creation_date"]

            new_author = Author()
            author_dict = schemes_dict["author"]
            new_author.author_name = author_dict["name"]
            new_scheme.author = new_author

            new_conclusion = Conclusion()
            conclusion_dict = schemes_dict["conclusion"]
            new_conclusion.id = conclusion_dict["id"]
            new_conclusion.description = conclusion_dict["description"]
            new_scheme.conclusion = new_conclusion

            new_scheme.premises = []
            premises_dicts = schemes_dict["dist_premises"]
            for dist_premise_dict in dist_premises_dicts:
                new_premise = Premise()
                new_premise.id = dist_premise_dict["id"]
                new_premise.name = dist_premise_dict["name"]
                new_premise.content = dist_premise_dict["content"]
                new_solution.dist_premises.append(new_premise)

            new_scheme.presumptions = []
            presumptions_dicts = solution_dict["presumptions"]
            for presumptions_dict in presumptions_dicts:
                new_premise = Premise()
                new_premise.id = presumptions_dict["id"]
                new_premise.name = presumptions_dict["name"]
                new_premise.content = presumptions_dict["content"]
                new_solution.presumptions.append(new_premise)

            new_scheme.exceptions = []
            exceptions_dicts = solution_dict["exceptions"]
            for exceptions_dict in exceptions_dicts:
                new_premise = Premise()
                new_premise.id = exceptions_dict["id"]
                new_premise.name = exceptions_dict["name"]
                new_premise.content = exceptions_dict["content"]
                new_solution.exceptions.append(new_premise)

            new_justification.schemes.append(new_scheme)

        new_justification.dialogue_graphs = []
        dialogue_graphs_dicts = justification_dict["dialog_graphs"]
        for dialogue_graphs_dict in dialogue_graphs_dicts:
            new_dialogue_graph = DialogueGraph()
            new_dialogue_graph.nodes = []
            nodes_dicts = dialogue_graphs_dict["nodes"]
            for node_dict in nodes_dicts:
                new_node = ArgNode(
                    node_dict["arg_case_id"],
                    node_dict["child_arg_cases_ids"],
                    node_dict["node_type"],
                    node_dict["parent_arg_case_id"]
                )
                new_dialogue_graph.nodes.append(new_node)
            new_justification.dialogue_graphs.append(new_dialogue_graph)

        new_argument_case = ArgumentCase(arg_id=argument_case_dict["id"],
                                         times_used=argument_case_dict["times_used"],
                                         creation_date=argument_case_dict["creation_date"],
                                         problem=new_problem,
                                         solution=new_solution,
                                         justification=new_justification)
        new_argument_cases.append(new_argument_case)
        count += 1

    save_objects(new_argument_cases, "argument_cases_py.dat")

    fh = open("argument_cases_py.dat", 'rb')
    logger.info("\n\n\nTodo el contenido del fichero:")
    count = 0
    inf = ""
    while True:
        try:
            arg_case: ArgumentCase = load(fh)
            inf += "Argument case ({})[{}]\n".format(count, type(arg_case))
            inf += "Times Used: {}\nCreationDate: {}\nID: {}\n".format(arg_case.times_used,
                                                                       arg_case.creation_date, arg_case.id)
            inf += "Problem: {}\n".format(arg_case.problem)
            inf += "Solution: {}\n".format(arg_case.solutions)
            inf += "Justification: {}\n".format(arg_case.justification)
            count += 1
        except EOFError:
            logger.info(inf)
            logger.info("Amount of ArgumentCase inside the file: {}".format(count))
            break
    fh.close()
