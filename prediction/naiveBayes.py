import os
import sys
sys.path.append("..")
from base.csv_operation import *
import math
import random
from collections import defaultdict


class BayesModel():
    def __init__(self, TRAIN_RATIO=1.0, model_path=os.path.abspath(os.path.join(os.getcwd(), "..")) + '/model/', data_path=os.path.abspath(os.path.join(os.getcwd(), "..")) + '/data/', dataSet=None, dataLabel=None):
        self.model_path = model_path
        self.data_path = data_path
        self.TRAIN_RATIO = TRAIN_RATIO
        self.dataSet = dataSet
        self.dataClass = dataLabel
        assert self.dataSet == None
        assert self.dataClass == None
        assert isinstance(self.dataSet, list)
        assert isinstance(self.dataClass, list)
        assert isinstance(self.dataClass, list)
        total_len = len(self.dataClass)
        basic_set = [i for i in range(0, total_len)]
        random.shuffle(basic_set)
        self.trainSet = [self.dataSet[i] for i in basic_set[0:int(total_len * self.TRAIN_RATIO)]]
        self.trainLabel = [self.dataClass[i] for i in basic_set[0:int(total_len * self.TRAIN_RATIO)]]
        self.testSet = [self.dataSet[i] for i in basic_set[int(total_len * self.TRAIN_RATIO):]]
        self.testLabel = [self.dataClass[i] for i in basic_set[int(total_len * self.TRAIN_RATIO):]]


    def mutual_info(self, m, n, p, q):
        return n * 1.0 / m * math.log(m, (n + 1) * 1.0 / (p * q)) / math.log(2)

    def construct_dict(self):
        return [0] * 2

    def __prepare(self):
        print("===========Prepare For Train Model=============")
        fw = open(self.model_path + "feature.txt", 'w')
        word_feature = defaultdict(self.construct_dict)
        label_feature = [0] * 2
        for i in range(len(self.dataSet)):
            label = int(self.dataClass[i])
            dataset = self.dataSet[i]
            for word in dataset:
                word_feature[word][label] += 1
                label_feature[label] += 1
        mDict = defaultdict(self.construct_dict)
        N = sum(label_feature)
        for k, vs in word_feature.items():
            for i in range(len(vs)):
                N11 = vs[i]
                N10 = sum(vs) - N11
                N01 = label_feature[i] - N11
                N00 = N - N11 - N10 - N01
                mi = self.mutual_info(N, N11, N10 + N11, N01 + N11) + self.mutual_info(N, N10, N10 + N11,
                                                                                       N00 + N10) + self.mutual_info(N, N01, N01 + N11,
                                                                                                                     N01 + N00) + self.mutual_info(
                    N, N00, N00 + N10, N00 + N01)
                mDict[k][i] = mi
        fWords = set()
        for i in range(len(label_feature)):
            keyf = lambda x: x[1][i]
            sortedDict = sorted(mDict.items(), key=keyf, reverse=True)
            for j in range(len(sortedDict)):
                fWords.add(sortedDict[j][0])
                fw.write(sortedDict[j][0] + ",")
        fw.write("\n")
        fw.write(str(label_feature[0]) + "," + str(label_feature[1]) + "\n")
        self.fWords = fWords
        self.label_feature = label_feature
        fw.close()


    def train_bayes(self):
        print("=========Training Model===========")
        self.__prepare()
        wordCount = defaultdict(self.construct_dict)
        docCounts = self.label_feature
        tCount = [0] * len(docCounts)
        for i in range(len(self.trainSet)):
            label, text = self.trainLabel[i], self.trainSet[i]
            for word in text:
                if word in self.fWords:
                    tCount[label] += 1
                    wordCount[word][label] += 1
        scores = {}
        for k, v in wordCount.items():
            score = [(v[i] + 1) * 1.0 / (tCount[i] + len(wordCount)) for i in range(len(v))]
            scores[k] = score
        self.scores = scores



    def save_model(self):
        print("===========Save Model==============")
        for key, value in self.scores.items():
            self.scores[key] = {0: value[0], 1: value[1]}
        write_to_csv(self.scores, self.model_path + "scores.csv", ['word', 'probability'])
        fw = open(self.model_path + "wordLabel.txt", 'w')
        for word in self.fWords:
            fw.write(word + ",")
        fw.write("\n")
        fw.write(str(self.label_feature[0]) + "," + str(self.label_feature[1]) + "\n")
        fw.close()


    def load_model(self):
        scores = read_to_dict(self.model_path)
        fr = open(self.feature_path)
        self.fWords = fr.readlines().split(',')
        self.scores = scores
        label_feature = open(self.label_path).readlines().split(',')
        label_feature = [int(label) for label in label_feature]
        self.label_feature = label_feature



    def predict_bayes(self, text):
        docCounts, features = self.label_feature, self.fWords
        docScores = [math.log(count * 1.0 / sum(docCounts)) for count in docCounts]
        print("==============Predicting===========")
        preValues = list(docScores)
        for word in text:
            if word in self.fWords:
                for i in range(len(preValues)):
                    preValues[i] += math.log(self.scores[word][i])

        m = max(preValues)
        print("===========Predict Value========" + preValues.index(m) + "===========")
        return preValues.index(m)


    def model_analysis(self):
        docCounts, features = self.label_feature, self.fWords
        docScores = [math.log(count * 1.0 / sum(docCounts)) for count in docCounts]
        rCount = 0
        docCount = 0
        pCount = 0
        nCount = 0
        p = 0
        n = 0
        print("==============Testing=============")
        for j in range(len(self.testSet)):
            text = self.testSet[j]
            label = self.testLabel[j]
            preValues = list(docScores)
            for word in text:
                if word in self.scores.keys():
                    for i in range(len(preValues)):
                        preValues[i] += math.log(self.scores[word][i])
            m = max(preValues)
            v = preValues.index(m)
            if int(v) == int(label):
                rCount += 1
            if int(label) == 1:
                p += 1
                if int(v) == 1: pCount += 1
            if int(label) == 0:
                n += 1
                if int(v) == 0: nCount += 1
            docCount += 1
        print("Test Sample: %d" % docCount, "Correct sample: %d" % rCount )
        print("Model Accuracy: %s" % str(rCount / docCount))
        print("Positive news Accuracy: %s" % str(pCount / p))
        print("Negative news Accuracy: %s" % str(nCount / n))

