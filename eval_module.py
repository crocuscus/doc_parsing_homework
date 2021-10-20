from typing import List, Dict
from statistics import mean
from sklearn.metrics import f1_score, accuracy_score
import re
from difflib import SequenceMatcher
import numpy as np
import os
import pickle
import json

from solution import Solution

BASE_DIR = "./train/txts"
BASE_GROUND_TRUE = "./train/gold_labels.txt"
TRAIN_RATIO = 0.8


def subtasks_improves(result: dict) -> int:
    BASELINE_SCORES = {
        'date_accuracy': 0.7996941896,
        'number_accuracy': 0.7262996942,
        'type_f1_score': 0.569159562,
        'name_jaccard': 0.7030790994,
        'authority_jaccard': 0.6447061931,
        'delta': 0.00001
    }
    subtasks_improves = int(len([metric for metric, value in result.items()
                             if BASELINE_SCORES[metric] + BASELINE_SCORES["delta"] < value]))
    return subtasks_improves    


def preprocess(text):
    text = text.lower()
    text = text.replace('\n', ' ')
    text = re.sub(" +", " ", text)
    return text


def string_jaccard_metric(gold_names, pred_names):
    scores = []
    for gold, pred in zip(gold_names, pred_names):
        if len(pred) == 0:
            scores.append(0)
            continue
        gold = gold.lower()
        pred = pred.lower()
        match = SequenceMatcher(None, gold, pred).find_longest_match(0, len(gold), 0, len(pred))

        gold_start_offset = match.a
        gold_end_offset = len(gold) - match.a - match.size
        pred_start_offset = match.b
        pred_end_offset = len(pred) - match.b - match.size
        score = match.size / (max([gold_end_offset, pred_end_offset]) + match.size + max([gold_start_offset, pred_start_offset]))
        scores.append(score)
    return mean(scores)


def quality(predicted: List[dict], expected: List[dict]):
    pred_dates, exp_dates, pred_names, exp_names, \
        pred_types, exp_types, pred_auths, exp_auths, pred_numbers, exp_numbers = ([] for _ in range(10))
    
    for pred, exp in zip(predicted, expected):

        pred_dates.append(pred['date'] if pred['date'] is not None else '')
        exp_dates.append(exp['date'])

        pred_numbers.append(pred['number'].lower() if pred['number'] is not None else '')
        exp_numbers.append(exp['number'].lower())

        pred_types.append(pred['type'] if pred['type'] is not None else '')
        exp_types.append(exp['type'])

        # authorities need to be normalized
        pred_auths.append(preprocess(pred['authority']) if pred['authority'] is not None else '')
        exp_auths.append(preprocess(exp['authority']))

        # names need to be normalized
        pred_names.append(preprocess(pred['name']) if pred['name'] is not None else '')
        exp_names.append(preprocess(exp['name']))

    date_accuracy = accuracy_score(exp_dates, pred_dates)
    
    number_accuracy = accuracy_score(exp_numbers, pred_numbers)

    type_f1 = f1_score(exp_types, pred_types, average='macro')

    name_jaccard = string_jaccard_metric(exp_names, pred_names)

    auth_jaccard = string_jaccard_metric(exp_auths, pred_auths)

    round_to = 10
    result = {
        'date_accuracy': float(round(date_accuracy, round_to)),
        'number_accuracy': float(round(number_accuracy, round_to)),
        'type_f1_score': float(round(type_f1, round_to)),
        'name_jaccard': float(round(name_jaccard, round_to)),
        'authority_jaccard': float(round(auth_jaccard, round_to))
    }
    result['subtasks_improves'] = subtasks_improves(result)
    
    return result


def prepare_test() -> None:
    if os.path.exists("tests_status.txt"):
        return

    ex_list = [x.split(".")[0] for x in os.listdir(BASE_DIR) if len(x.split(".")) == 2]
    np.random.shuffle(ex_list)

    train_ind = ex_list[:int(len(ex_list) * TRAIN_RATIO)]
    test_ind = ex_list[int(len(ex_list) * TRAIN_RATIO):]
    print("Sizes of sets (train / test)", len(train_ind), len(test_ind))

    pickle.dump(train_ind, open("train_index.pkl", "wb"))
    pickle.dump(test_ind, open("test_index.pkl", "wb"))

    pickle.dump({"test_ready": True}, open("tests_status.txt", "wb"))


def read_data(t: str) -> List[str]:
    assert t in ["test", "train"]
    ind = pickle.load(open(f"{t}_index.pkl", "rb"))

    return sorted(
        (file_name.split(".")[0], open(os.path.join(BASE_DIR, file_name), "r").read())
        for file_name in os.listdir(BASE_DIR) if file_name.split(".")[0] in ind
    )


def read_ground_true(t: str) -> List[Dict[str, str]]:
    assert t in ["test", "train"]
    ind = pickle.load(open(f"{t}_index.pkl", "rb"))

    every = open(BASE_GROUND_TRUE, "r").readlines()
    return sorted((
            json.loads(value)
            for value in every
            if json.loads(value)["id"] in ind
        ),
        key=lambda x: x["id"]
    )


def run_evaluation(t: str = "test"):
    prepare_test()
    _data = read_data(t)
    _ground_true: List[Dict] = read_ground_true(t)
    ind = pickle.load(open(f"{t}_index.pkl", "rb"))
    np.random.shuffle(ind)

    data = []
    ground_true = []
    for i in ind:
        if i in [x[0] for x in _data] and i in  [x["id"] for x in _ground_true]:
            data += [x[1] for x in _data if x[0] == i]
            ground_true += [x["label"] for x in _ground_true if x["id"] == i]



    predict: List[Dict] = Solution().predict(data)

    for i in range(len(predict)):
        if predict[i]["name"] != ground_true[i] ["name"].lower():
            print(data[i], predict[i], ground_true[i], sep="\n")
            break

    result = quality(predict, ground_true)

    print(result)


def run_one_test():
    file_name = "586fb5f26e9a43c9d9f8de4afcf098b7f58dc1ff.txt"
    test = open(os.path.join(BASE_DIR, file_name), "r").read()
    print(Solution().predict([test]))

# run_one_test()

run_evaluation()

